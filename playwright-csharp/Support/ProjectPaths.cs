namespace Fictoshop.PlaywrightTests.Support;

public static class ProjectPaths
{
    public static string Root { get; } = FindProjectRoot();

    public static string Python => Path.Combine(Root, ".venv", "bin", "python");

    private static string FindProjectRoot()
    {
        var candidates = new[] { Directory.GetCurrentDirectory(), AppContext.BaseDirectory };
        foreach (var candidate in candidates)
        {
            var directory = new DirectoryInfo(candidate);
            while (directory is not null)
            {
                if (File.Exists(Path.Combine(directory.FullName, "manage.py")))
                {
                    return directory.FullName;
                }

                directory = directory.Parent;
            }
        }

        throw new DirectoryNotFoundException("Could not locate the Fictoshop root containing manage.py.");
    }
}
