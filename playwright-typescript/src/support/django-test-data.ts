import { execFile } from "node:child_process";
import { randomUUID } from "node:crypto";
import fs from "node:fs";
import { promisify } from "node:util";
import { projectPaths } from "./project-paths.js";
import type {
  Credentials,
  DatabaseSnapshot,
  OrderRecord,
  ProductRecord,
  ReviewRecord
} from "./models.js";

const execFileAsync = promisify(execFile);
const jsonMarker = "__FICTOSHOP_JSON__";

export class DjangoTestData {
  snapshot(): Promise<DatabaseSnapshot> {
    return this.executeJson<DatabaseSnapshot>(
      "from django.contrib.auth import get_user_model; from shop.models import Order,Product,Review; " +
      `print('${jsonMarker}'+json.dumps({'orders':list(Order.objects.values_list('id',flat=True)),'reviews':list(Review.objects.values_list('id',flat=True)),'products':list(Product.objects.values_list('id',flat=True)),'users':list(get_user_model().objects.values_list('id',flat=True))}))`
    );
  }

  cleanup(snapshot: DatabaseSnapshot): Promise<void> {
    const code =
      "from pathlib import Path; from django.contrib.auth import get_user_model; from shop.models import Order,Product,Review; " +
      `new_products=list(Product.objects.exclude(id__in=${this.list(snapshot.products)})); ` +
      "image_paths=[Path(p.image_url.path) for p in new_products if p.image_url]; " +
      `Order.objects.exclude(id__in=${this.list(snapshot.orders)}).delete(); ` +
      `Review.objects.exclude(id__in=${this.list(snapshot.reviews)}).delete(); ` +
      `Product.objects.exclude(id__in=${this.list(snapshot.products)}).delete(); ` +
      `get_user_model().objects.exclude(id__in=${this.list(snapshot.users)}).delete(); ` +
      "[(p.unlink(missing_ok=True)) for p in image_paths if p.exists() and '_' in p.stem]";
    return this.execute(code);
  }

  async createUser(superuser: boolean): Promise<Credentials> {
    const reference = randomUUID().replaceAll("-", "").slice(0, 8);
    const username = `typescript_${superuser ? "admin" : "user"}_${reference}`;
    const password = `Playwright-${randomUUID()}!`;
    const method = superuser ? "create_superuser" : "create_user";
    const code =
      "from django.contrib.auth import get_user_model; " +
      `u=get_user_model().objects.${method}(username=${this.py(username)},email=${this.py(`${username}@example.com`)},password=${this.py(password)}); ` +
      `print('${jsonMarker}'+json.dumps({'username':u.username,'password':${this.py(password)},'superuser':${superuser ? "True" : "False"}}))`;
    return this.executeJson<Credentials>(code);
  }

  createProduct(name: string, description: string, price: number, stock: number): Promise<ProductRecord> {
    const code =
      "from shop.models import Product; " +
      `p=Product.objects.create(name=${this.py(name)},description=${this.py(description)},price=${this.py(price.toFixed(2))},in_stock=${stock}); ` +
      `print('${jsonMarker}'+json.dumps({'id':p.id,'name':p.name,'description':p.description,'price':str(p.price),'in_stock':p.in_stock}))`;
    return this.executeJson<ProductRecord>(code).then(this.normalizeProduct);
  }

  createReview(product: ProductRecord, user: Credentials, rating: number, comment: string): Promise<ReviewRecord> {
    const code =
      "from django.contrib.auth import get_user_model; from shop.models import Product,Review; " +
      `u=get_user_model().objects.get(username=${this.py(user.username)}); p=Product.objects.get(id=${product.id}); ` +
      `r=Review.objects.create(product=p,user=u,rating=${this.py(rating.toFixed(1))},comment=${this.py(comment)}); ` +
      `print('${jsonMarker}'+json.dumps({'id':r.id,'user':u.username,'rating':str(r.rating),'comment':r.comment}))`;
    return this.executeJson<ReviewRecord>(code).then((review) => ({ ...review, rating: Number(review.rating) }));
  }

  createOrder(): Promise<OrderRecord> {
    const reference = randomUUID().replaceAll("-", "").slice(0, 8);
    const code =
      "from shop.models import Order,OrderItem; " +
      `o=Order.objects.create(full_name=${this.py(`Playwright Customer ${reference}`)},email=${this.py(`customer-${reference}@example.com`)},phone='+47 99887766',address='Testveien 42',postal_code='0123',city='Oslo',country='Norway',total_amount='84.97'); ` +
      `OrderItem.objects.create(order=o,product_name=${this.py(`Test shoes ${reference}`)},unit_price='29.99',quantity=2,line_total='59.98'); ` +
      `OrderItem.objects.create(order=o,product_name=${this.py(`Test bottle ${reference}`)},unit_price='24.99',quantity=1,line_total='24.99'); ` +
      `print('${jsonMarker}'+json.dumps({'id':o.id,'full_name':o.full_name,'email':o.email,'phone':o.phone,'address':o.address,'postal_code':o.postal_code,'city':o.city,'country':o.country,'total_amount':str(o.total_amount),'items':[{'product_name':i.product_name,'unit_price':str(i.unit_price),'quantity':i.quantity,'line_total':str(i.line_total)} for i in o.items.all()]}))`;
    return this.executeJson<OrderRecord>(code).then((order) => ({
      ...order,
      total_amount: Number(order.total_amount),
      items: order.items.map((item) => ({
        ...item,
        unit_price: Number(item.unit_price),
        line_total: Number(item.line_total)
      }))
    }));
  }

  getProductStock(productId: number): Promise<number> {
    return this.executeJson<number>(`from shop.models import Product; print('${jsonMarker}'+json.dumps(Product.objects.get(id=${productId}).in_stock))`);
  }

  setProductStock(productId: number, stock: number): Promise<void> {
    return this.execute(`from shop.models import Product; Product.objects.filter(id=${productId}).update(in_stock=${stock})`);
  }

  countOrders(): Promise<number> {
    return this.executeJson<number>(`from shop.models import Order; print('${jsonMarker}'+json.dumps(Order.objects.count()))`);
  }

  countReviews(productId: number, username: string): Promise<number> {
    return this.executeJson<number>(
      `from shop.models import Review; print('${jsonMarker}'+json.dumps(Review.objects.filter(product_id=${productId},user__username=${this.py(username)}).count()))`
    );
  }

  async findProductByName(name: string): Promise<ProductRecord | null> {
    const product = await this.executeJson<ProductRecord | null>(
      "from shop.models import Product; " +
      `p=Product.objects.filter(name=${this.py(name)}).first(); print('${jsonMarker}'+json.dumps(None if p is None else {'id':p.id,'name':p.name,'description':p.description,'price':str(p.price),'in_stock':p.in_stock}))`
    );
    return product ? this.normalizeProduct(product) : null;
  }

  private normalizeProduct(product: ProductRecord): ProductRecord {
    return { ...product, price: Number(product.price), in_stock: Number(product.in_stock) };
  }

  private async executeJson<T>(code: string): Promise<T> {
    const output = await this.run(`import json; ${code}`);
    const line = output.split(/\r?\n/).findLast((value) => value.startsWith(jsonMarker));
    if (!line) {
      throw new Error(`Django command returned no JSON marker. Output:\n${output}`);
    }
    return JSON.parse(line.slice(jsonMarker.length)) as T;
  }

  private async execute(code: string): Promise<void> {
    await this.run(code);
  }

  private async run(code: string): Promise<string> {
    if (!fs.existsSync(projectPaths.python)) {
      throw new Error(`Django virtual environment not found: ${projectPaths.python}`);
    }
    const { stdout, stderr } = await execFileAsync(
      projectPaths.python,
      [projectPaths.managePy, "shell", "-c", code],
      { cwd: projectPaths.root, maxBuffer: 10 * 1024 * 1024 }
    );
    if (stderr && process.env.DEBUG_DJANGO_FIXTURES === "true") {
      process.stderr.write(stderr);
    }
    return stdout;
  }

  private py(value: string): string {
    return JSON.stringify(value);
  }

  private list(values: number[]): string {
    return `[${values.join(",")}]`;
  }
}
