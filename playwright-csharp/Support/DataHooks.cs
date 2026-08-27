using Reqnroll;

namespace Fictoshop.PlaywrightTests.Support;

[Binding]
public sealed class DataHooks
{
    private readonly ScenarioContext _scenarioContext;
    private DjangoTestData? _data;
    private DatabaseSnapshot? _snapshot;
    private StorefrontApi? _api;

    public DataHooks(ScenarioContext scenarioContext)
    {
        _scenarioContext = scenarioContext;
    }

    [BeforeScenario(Order = 10)]
    public async Task PrepareAsync()
    {
        _data = new DjangoTestData();
        _snapshot = await _data.SnapshotAsync();
        _api = new StorefrontApi();
        _scenarioContext.Set(_data);
        _scenarioContext.Set(_api);
        _scenarioContext.Set(new ScenarioState());
    }

    [AfterScenario(Order = 50)]
    public async Task CleanupAsync()
    {
        try
        {
            if (_api is not null)
            {
                await _api.DeleteAsync("/cart");
            }

            if (_data is not null && _snapshot is not null)
            {
                await _data.CleanupAsync(_snapshot);
            }
        }
        finally
        {
            _api?.Dispose();
        }
    }
}
