module.exports = {
  apps : [
    {
      name: "timer",
      script: "timer.py",
      cwd: "./",
      interpreter: "python", // Use Python from the current environment
    },
    {
      name: "account_backend",
      script: "app.py",
      cwd: "./account_backend/",
      interpreter: "python",
    },
    {
      name: "serve_backend",
      script: "app.py",
      cwd: "./serve_backend/",
      interpreter: "python",
    },
    {
      name: "visual_backend",
      script: "streamlit",
      args: ["run", "app_notiles.py", "--server.headless", "true"], // You can also use app_tiles.py with custom tile map functionality.
      cwd: "./visual_backend/",
      interpreter: "python", 
    },

    // If using app_tiles.py, you need to start cors_server.py
    {
      name: "cors_server",
      script: "cors_server.py",
      cwd: "./visual_backend/tiles",
      interpreter: "python",
    }
  ]
};
