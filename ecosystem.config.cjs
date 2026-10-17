const path = require('node:path');

const root = __dirname;
const python = path.join(root, '.venv', 'bin', 'python');

module.exports = {
  apps: [
    {
      name: 'traffic-camera',
      cwd: root,
      script: path.join(root, 'run_camera.py'),
      interpreter: python,
      autorestart: true,
      min_uptime: '10s',
      max_restarts: 5,
      restart_delay: 5000,
    },
    {
      name: 'traffic-web',
      cwd: root,
      script: python,
      interpreter: 'none',
      args: '-m uvicorn web_server.server:app --host 0.0.0.0 --port 8000',
      autorestart: true,
      min_uptime: '10s',
      max_restarts: 5,
      restart_delay: 5000,
    },
  ],
};
