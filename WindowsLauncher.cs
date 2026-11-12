using System;
using System.Diagnostics;
using System.IO;
using System.IO.Compression;
using System.Reflection;
using System.Security.Cryptography;
using System.Windows.Forms;

internal static class WindowsLauncher
{
    [STAThread]
    private static int Main(string[] args)
    {
        bool selfTest = args.Length == 2 && args[0] == "--self-test";
        try
        {
            if (args.Length != 0 && !selfTest)
            {
                throw new ArgumentException("Usage: ModelRoom.exe [--self-test report.json]");
            }
            string runtime = GetRuntime();

            var info = new ProcessStartInfo
            {
                FileName = Path.Combine(runtime, "pythonw.exe"),
                Arguments = selfTest ? "-I -B -m room_selftest" : "-I -B -m model_room",
                WorkingDirectory = runtime,
                UseShellExecute = false,
                CreateNoWindow = true
            };
            if (selfTest)
            {
                info.EnvironmentVariables["MODELROOM_SELFTEST_REPORT"] = Path.GetFullPath(args[1]);
            }
            using (Process app = Process.Start(info))
            {
                app.WaitForExit();
                if (app.ExitCode == 0)
                {
                    return 0;
                }
                throw new InvalidOperationException("The app exited with code " + app.ExitCode + ".");
            }
        }
        catch (Exception error)
        {
            if (selfTest) return 1;
            MessageBox.Show("Model Room could not start.\n\n" + error.Message,
                "Model Room", MessageBoxButtons.OK, MessageBoxIcon.Error);
            return 1;
        }
    }

    private static Stream OpenBundle()
    {
        return Assembly.GetExecutingAssembly().GetManifestResourceStream("ModelRoom.Runtime");
    }

    private static string GetRuntime()
    {
        string fingerprint;
        using (Stream resource = OpenBundle())
        using (SHA256 sha = SHA256.Create())
        {
            fingerprint = BitConverter.ToString(sha.ComputeHash(resource)).Replace("-", "").Substring(0, 24);
        }

        // Keep the listener executable at a stable path so private-network rules can be reused.
        string cache = Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.LocalApplicationData),
            "ModelRoom", "runtime");
        Directory.CreateDirectory(cache);
        string runtime = Path.Combine(cache, fingerprint);
        string ready = Path.Combine(runtime, ".ready");
        if (File.Exists(ready))
        {
            return runtime;
        }

        string staged = Path.Combine(cache, fingerprint + "-" + Guid.NewGuid().ToString("N"));
        try
        {
            Directory.CreateDirectory(staged);
            string archive = Path.Combine(staged, "runtime.zip");
            using (Stream resource = OpenBundle())
            using (FileStream output = File.Create(archive))
            {
                resource.CopyTo(output);
            }
            ZipFile.ExtractToDirectory(archive, staged);
            File.Delete(archive);
            File.WriteAllText(Path.Combine(staged, ".ready"), fingerprint);
            try
            {
                Directory.Move(staged, runtime);
            }
            catch (IOException)
            {
                if (!File.Exists(ready))
                {
                    throw;
                }
            }
            return runtime;
        }
        finally
        {
            try
            {
                if (Directory.Exists(staged))
                {
                    Directory.Delete(staged, true);
                }
            }
            catch (IOException) { }
            catch (UnauthorizedAccessException) { }
        }
    }
}
