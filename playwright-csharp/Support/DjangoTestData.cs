using System.Diagnostics;
using System.Globalization;
using System.Text.Json;

namespace Fictoshop.PlaywrightTests.Support;

public sealed class DjangoTestData
{
    private const string JsonMarker = "__FICTOSHOP_JSON__";
    private static readonly JsonSerializerOptions JsonOptions = new()
    {
        PropertyNameCaseInsensitive = true,
        NumberHandling = System.Text.Json.Serialization.JsonNumberHandling.AllowReadingFromString,
    };

    public Task<DatabaseSnapshot> SnapshotAsync() => ExecuteJsonAsync<DatabaseSnapshot>(
        "from django.contrib.auth import get_user_model; from shop.models import Order,Product,Review; " +
        "print('" + JsonMarker + "'+json.dumps({'orders':list(Order.objects.values_list('id',flat=True)),'reviews':list(Review.objects.values_list('id',flat=True)),'products':list(Product.objects.values_list('id',flat=True)),'users':list(get_user_model().objects.values_list('id',flat=True))}))");

    public Task CleanupAsync(DatabaseSnapshot snapshot)
    {
        var orders = PythonList(snapshot.Orders);
        var reviews = PythonList(snapshot.Reviews);
        var products = PythonList(snapshot.Products);
        var users = PythonList(snapshot.Users);
        var code =
            "from pathlib import Path; from django.contrib.auth import get_user_model; from shop.models import Order,Product,Review; " +
            $"new_products=list(Product.objects.exclude(id__in={products})); " +
            "image_paths=[Path(p.image_url.path) for p in new_products if p.image_url]; " +
            $"Order.objects.exclude(id__in={orders}).delete(); Review.objects.exclude(id__in={reviews}).delete(); Product.objects.exclude(id__in={products}).delete(); get_user_model().objects.exclude(id__in={users}).delete(); " +
            "[(path.unlink(missing_ok=True)) for path in image_paths if path.exists() and '_' in path.stem]";
        return ExecuteAsync(code);
    }

    public async Task<Credentials> CreateUserAsync(bool superuser)
    {
        var reference = Guid.NewGuid().ToString("N")[..8];
        var username = $"csharp_{(superuser ? "admin" : "user")}_{reference}";
        var password = $"Playwright-{Guid.NewGuid():N}!";
        var method = superuser ? "create_superuser" : "create_user";
        var code =
            "from django.contrib.auth import get_user_model; " +
            $"u=get_user_model().objects.{method}(username={Py(username)},email={Py(username + "@example.com")},password={Py(password)}); " +
            $"print('{JsonMarker}'+json.dumps({{'username':u.username,'password':{Py(password)}}}))";
        var result = await ExecuteJsonAsync<Dictionary<string, string>>(code);
        return new Credentials(result["username"], result["password"]);
    }

    public Task<ProductRecord> CreateProductAsync(
        string name,
        string description,
        decimal price,
        int stock)
    {
        var code =
            "from shop.models import Product; " +
            $"p=Product.objects.create(name={Py(name)},description={Py(description)},price={Py(price.ToString(CultureInfo.InvariantCulture))},in_stock={stock}); " +
            $"print('{JsonMarker}'+json.dumps({{'id':p.id,'name':p.name,'description':p.description,'price':str(p.price),'in_stock':p.in_stock}}))";
        return ExecuteJsonAsync<ProductRecord>(code);
    }

    public Task<ReviewRecord> CreateReviewAsync(ProductRecord product, Credentials user, decimal rating, string comment)
    {
        var code =
            "from django.contrib.auth import get_user_model; from shop.models import Product,Review; " +
            $"u=get_user_model().objects.get(username={Py(user.Username)}); p=Product.objects.get(id={product.Id}); " +
            $"r=Review.objects.create(product=p,user=u,rating={Py(rating.ToString(CultureInfo.InvariantCulture))},comment={Py(comment)}); " +
            $"print('{JsonMarker}'+json.dumps({{'id':r.id,'user':u.username,'rating':str(r.rating),'comment':r.comment}}))";
        return ExecuteJsonAsync<ReviewRecord>(code);
    }

    public Task<OrderRecord> CreateOrderAsync()
    {
        var reference = Guid.NewGuid().ToString("N")[..8];
        var code =
            "from shop.models import Order,OrderItem; " +
            $"o=Order.objects.create(full_name={Py("Playwright Customer " + reference)},email={Py("customer-" + reference + "@example.com")},phone='+47 99887766',address='Testveien 42',postal_code='0123',city='Oslo',country='Norway',total_amount='84.97'); " +
            $"a=OrderItem.objects.create(order=o,product_name={Py("Test shoes " + reference)},unit_price='29.99',quantity=2,line_total='59.98'); " +
            $"b=OrderItem.objects.create(order=o,product_name={Py("Test bottle " + reference)},unit_price='24.99',quantity=1,line_total='24.99'); " +
            $"print('{JsonMarker}'+json.dumps({{'id':o.id,'full_name':o.full_name,'email':o.email,'phone':o.phone,'address':o.address,'postal_code':o.postal_code,'city':o.city,'country':o.country,'total_amount':str(o.total_amount),'items':[{{'product_name':i.product_name,'unit_price':str(i.unit_price),'quantity':i.quantity,'line_total':str(i.line_total)}} for i in o.items.all()]}}))";
        return ExecuteJsonAsync<OrderRecord>(code);
    }

    public Task<int> GetProductStockAsync(int productId) => ExecuteJsonAsync<int>(
        $"from shop.models import Product; print('{JsonMarker}'+json.dumps(Product.objects.get(id={productId}).in_stock))");

    public Task SetProductStockAsync(int productId, int stock) => ExecuteAsync(
        $"from shop.models import Product; Product.objects.filter(id={productId}).update(in_stock={stock})");

    public Task<int> CountOrdersAsync() => ExecuteJsonAsync<int>(
        $"from shop.models import Order; print('{JsonMarker}'+json.dumps(Order.objects.count()))");

    public Task<int> CountReviewsAsync(int productId, string username) => ExecuteJsonAsync<int>(
        "from shop.models import Review; " +
        $"print('{JsonMarker}'+json.dumps(Review.objects.filter(product_id={productId},user__username={Py(username)}).count()))");

    public Task<ProductRecord?> FindProductByNameAsync(string name) => ExecuteJsonAsync<ProductRecord?>(
        "from shop.models import Product; " +
        $"p=Product.objects.filter(name={Py(name)}).first(); print('{JsonMarker}'+json.dumps(None if p is None else {{'id':p.id,'name':p.name,'description':p.description,'price':str(p.price),'in_stock':p.in_stock}}))");

    private async Task<T> ExecuteJsonAsync<T>(string code)
    {
        var output = await ExecuteProcessAsync("import json; " + code);
        var line = output.Split('\n', StringSplitOptions.RemoveEmptyEntries)
            .LastOrDefault(value => value.StartsWith(JsonMarker, StringComparison.Ordinal));
        if (line is null)
        {
            throw new InvalidOperationException($"Django command returned no JSON marker. Output:\n{output}");
        }

        return JsonSerializer.Deserialize<T>(line[JsonMarker.Length..], JsonOptions)
            ?? throw new InvalidOperationException("Django command returned an empty JSON value.");
    }

    private async Task ExecuteAsync(string code) => await ExecuteProcessAsync(code);

    private static async Task<string> ExecuteProcessAsync(string code)
    {
        if (!File.Exists(ProjectPaths.Python))
        {
            throw new FileNotFoundException("The Django virtual environment was not found.", ProjectPaths.Python);
        }

        var startInfo = new ProcessStartInfo
        {
            FileName = ProjectPaths.Python,
            WorkingDirectory = ProjectPaths.Root,
            RedirectStandardOutput = true,
            RedirectStandardError = true,
            UseShellExecute = false,
        };
        startInfo.ArgumentList.Add("manage.py");
        startInfo.ArgumentList.Add("shell");
        startInfo.ArgumentList.Add("-c");
        startInfo.ArgumentList.Add(code);

        using var process = Process.Start(startInfo)
            ?? throw new InvalidOperationException("Could not start Django test-data process.");
        var stdoutTask = process.StandardOutput.ReadToEndAsync();
        var stderrTask = process.StandardError.ReadToEndAsync();
        await process.WaitForExitAsync();
        var stdout = await stdoutTask;
        var stderr = await stderrTask;
        if (process.ExitCode != 0)
        {
            throw new InvalidOperationException($"Django test-data command failed ({process.ExitCode}).\n{stderr}\n{stdout}");
        }

        return stdout;
    }

    private static string Py(string value) => JsonSerializer.Serialize(value);

    private static string PythonList(IEnumerable<int> values) => $"[{string.Join(',', values)}]";
}
