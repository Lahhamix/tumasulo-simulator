from flask import Flask, request, jsonify, render_template_string
from simulator import Simulator
import tempfile
import os
import subprocess

app = Flask(__name__)
simulator = None  # Global simulator instance

HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>Tomasulo Simulator</title>
  <link href='https://fonts.googleapis.com/css?family=Roboto:400,700&display=swap' rel='stylesheet'>
  <style>
    body {
      background: linear-gradient(120deg, #3b82f6 0%, #facc15 100%);
      margin: 0; padding: 0;
      font-family: 'Roboto', Arial, sans-serif;
      min-height: 100vh;
    }
    .container {
      background: #f9fafb;
      max-width: 1200px;
      margin: 48px auto 24px auto;
      border-radius: 18px;
      box-shadow: 0 8px 36px rgba(44,62,80,0.13);
      padding: 40px 44px 38px 44px;
      position: relative;
      animation: fadeIn 0.7s;
    }
    @keyframes fadeIn {
      from { opacity: 0; transform: translateY(30px); }
      to { opacity: 1; transform: translateY(0); }
    }
    .logo {
      display: flex;
      align-items: center;
      justify-content: center;
      margin-bottom: 18px;
    }
    .logo-icon {
      width: 40px; height: 40px;
      margin-right: 13px;
      filter: drop-shadow(0 2px 8px #3b82f633);
    }
    h1 {
      color: #232946;
      text-align: center;
      margin-bottom: 18px;
      letter-spacing: 1px;
      font-size: 2.2em;
      font-weight: 700;
    }
    label {
      font-weight: 700;
      color: #232946;
      margin-top: 18px;
      display: block;
      margin-bottom: 6px;
    }
    textarea {
      width: 100%;
      min-height: 120px;
      font-family: monospace;
      font-size: 15px;
      border: 1.5px solid #bfc9d1;
      border-radius: 8px;
      padding: 13px;
      margin-bottom: 12px;
      background: #f3f6fa;
      transition: border 0.2s;
      resize: vertical;
      color: #232946;
    }
    textarea:focus {
      border: 1.5px solid #3b82f6;
      outline: none;
    }
    input[type='file'] {
      margin: 10px 0 18px 0;
    }
    button {
      background: linear-gradient(90deg, #3b82f6 0%, #facc15 100%);
      color: #fff;
      border: none;
      border-radius: 8px;
      padding: 14px 34px;
      font-size: 17px;
      font-weight: bold;
      cursor: pointer;
      margin-top: 10px;
      box-shadow: 0 2px 10px rgba(59,130,246,0.10);
      transition: background 0.2s, transform 0.1s;
      letter-spacing: 0.5px;
    }
    button:hover {
      background: linear-gradient(90deg, #facc15 0%, #3b82f6 100%);
      transform: translateY(-2px) scale(1.04);
    }
    .gen-btn {
      background: linear-gradient(90deg, #facc15 0%, #3b82f6 100%);
      color: #fff;
      border: none;
      border-radius: 8px;
      padding: 12px 28px;
      font-size: 16px;
      font-weight: bold;
      cursor: pointer;
      margin: 0 0 18px 0;
      box-shadow: 0 2px 10px rgba(250,204,21,0.10);
      transition: background 0.2s, transform 0.1s;
      letter-spacing: 0.5px;
      display: block;
    }
    .gen-btn:hover {
      background: linear-gradient(90deg, #3b82f6 0%, #facc15 100%);
      color: #fff;
      transform: translateY(-2px) scale(1.04);
    }
    .output {
      margin-top: 38px;
      background: #f3f6fa;
      border-radius: 12px;
      box-shadow: 0 2px 12px rgba(59,130,246,0.08);
      padding: 20px 20px 12px 20px;
      transition: box-shadow 0.2s;
      position: relative;
    }
    .output.collapsed {
      max-height: 48px;
      overflow: hidden;
      padding-bottom: 0;
    }
    .toggle-btn {
      display: block;
      margin: 0 0 10px auto;
      background: none;
      border: none;
      color: #3b82f6;
      font-size: 1.1em;
      cursor: pointer;
      font-weight: bold;
      transition: color 0.2s;
      padding: 0 8px;
    }
    .toggle-btn:hover {
      color: #facc15;
    }
    .gen-result {
      color: #3b82f6;
      font-weight: bold;
      margin: 10px 0 0 0;
      text-align: center;
      font-size: 1.08em;
      min-height: 24px;
    }
    h2 {
      color: #3b82f6;
      margin-top: 0;
      font-size: 1.2em;
      font-weight: 700;
    }
    h3 {
      color: #232946;
      margin: 0 0 12px 0;
      font-size: 1.1em;
      font-weight: 600;
    }
    pre {
      background: #fff;
      color: #232946;
      padding: 18px;
      border-radius: 8px;
      font-size: 15px;
      overflow-x: auto;
      margin: 0;
      font-family: 'Roboto Mono', monospace;
      box-shadow: 0 1px 4px #e0e7ff33;
    }
    pre div {
      padding: 8px;
      margin: 4px 0;
      border-radius: 4px;
      background: #f3f6fa;
      border-left: 3px solid #3b82f6;
    }
    .cycle-info {
      background: #dbeafe;
      color: #232946;
      padding: 12px;
      border-radius: 8px;
      margin-bottom: 16px;
      font-weight: bold;
      display: flex;
      justify-content: space-between;
      align-items: center;
    }
    .registers-section {
      background: #fff;
      border-radius: 8px;
      padding: 16px;
      margin-bottom: 16px;
      box-shadow: 0 1px 4px rgba(0,0,0,0.05);
    }
    .registers-grid {
      display: grid;
      grid-template-columns: repeat(4, 1fr);
      gap: 8px;
      margin-top: 8px;
    }
    .register-item {
      background: #f3f6fa;
      padding: 8px;
      border-radius: 4px;
      text-align: center;
      transition: transform 0.2s;
    }
    .register-item:hover {
      transform: translateY(-2px);
      box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    }
    .register-name {
      font-weight: bold;
      color: #3b82f6;
    }
    .register-value {
      color: #232946;
      font-size: 1.1em;
      margin: 4px 0;
    }
    .register-status {
      font-size: 0.9em;
      color: #facc15;
    }
    .rs-section {
      background: #fff;
      border-radius: 8px;
      padding: 16px;
      margin-bottom: 16px;
      box-shadow: 0 1px 4px rgba(0,0,0,0.05);
    }
    .rs-grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
      gap: 12px;
      margin-top: 8px;
    }
    .rs-item {
      background: #f3f6fa;
      padding: 12px;
      border-radius: 6px;
      border-left: 3px solid #3b82f6;
      transition: transform 0.2s;
    }
    .rs-item:hover {
      transform: translateY(-2px);
      box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    }
    .rs-name {
      font-weight: bold;
      color: #3b82f6;
      margin-bottom: 4px;
      font-size: 1.1em;
    }
    .rs-details {
      display: grid;
      grid-template-columns: auto 1fr;
      gap: 8px;
      font-size: 0.9em;
    }
    .rs-label {
      color: #666;
    }
    .rs-value {
      color: #232946;
    }
    .rs-value.waiting {
      color: #facc15;
      font-style: italic;
    }
    .cdb-section {
      background: #fff;
      border-radius: 8px;
      padding: 16px;
      margin-bottom: 16px;
      box-shadow: 0 1px 4px rgba(0,0,0,0.05);
    }
    .cdb-active {
      background: #dbeafe;
      color: #232946;
      padding: 12px;
      border-radius: 6px;
      font-weight: bold;
      text-align: center;
      animation: pulse 2s infinite;
    }
    .cdb-inactive {
      color: #666;
      text-align: center;
      font-style: italic;
    }
    @keyframes pulse {
      0% { box-shadow: 0 0 0 0 rgba(59,130,246,0.4); }
      70% { box-shadow: 0 0 0 10px rgba(59,130,246,0); }
      100% { box-shadow: 0 0 0 0 rgba(59,130,246,0); }
    }
    .simulation-complete {
      text-align: center;
      margin-top: 20px;
      padding: 16px;
      background: #dbeafe;
      border-radius: 8px;
      color: #232946;
      font-weight: bold;
      animation: fadeIn 0.5s;
    }
    .metrics-section {
      background: #fff;
      border-radius: 8px;
      padding: 16px;
      margin-top: 16px;
      box-shadow: 0 1px 4px rgba(0,0,0,0.05);
    }
    .metrics-grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
      gap: 12px;
      margin-top: 8px;
    }
    .metric-item {
      background: #f3f6fa;
      padding: 12px;
      border-radius: 6px;
      text-align: center;
    }
    .metric-label {
      color: #666;
      font-size: 0.9em;
      margin-bottom: 4px;
    }
    .metric-value {
      color: #3b82f6;
      font-size: 1.2em;
      font-weight: bold;
    }
    footer {
      text-align: center;
      color: #bfc9d1;
      font-size: 1em;
      margin: 18px 0 10px 0;
      letter-spacing: 0.5px;
    }
    @media (max-width: 800px) {
      .container { padding: 18px 6vw; }
      .registers-grid {
        grid-template-columns: repeat(2, 1fr);
      }
    }
    /* SVG logo color update */
    .logo-icon circle {
      fill: #3b82f6;
      stroke: #facc15;
    }
    .logo-icon path {
      stroke: #fff;
    }
  </style>
</head>
<body>
  <div class="container">
    <div class="logo">
      <svg class="logo-icon" viewBox="0 0 48 48" fill="none" xmlns="http://www.w3.org/2000/svg"><circle cx="24" cy="24" r="22" fill="#3b82f6" stroke="#facc15" stroke-width="3" /><path d="M16 32L32 16M16 16h16v16" stroke="#fff" stroke-width="3" stroke-linecap="round" stroke-linejoin="round" /></svg>
      <h1>Tomasulo Simulator</h1>
    </div>
    <button class="gen-btn" id="genBtn" type="button">Generate Random Traces</button>
    <div class="gen-result" id="genResult"></div>
    <form id="simForm">
      <label for="trace">Paste your trace here:</label>
      <textarea id="trace" name="trace" placeholder="ADD R1, R2, R3&#10;LOAD R4, 0(R5)&#10;..."></textarea>
      <label for="traceFile">Or upload a trace file:</label>
      <input type="file" id="traceFile" name="traceFile" accept=".txt"><br>
      <button type="submit">Run Simulation</button>
      <button type="button" id="stepBtn">Start Step Simulation</button>
      <button type="button" id="nextStepBtn" disabled>Next Step</button>
      <button type="button" id="resetBtn" disabled>Reset</button>
    </form>
    <div class="output" id="outputBox">
      <h2>Output:</h2>
      <button class="toggle-btn" id="toggleBtn" type="button">Hide Output</button>
      <pre id="output"></pre>
    </div>
  </div>
  <footer>
    Tumasulo Simulator - Clara & Hadi
  </footer>
  <script>
    let collapsed = false;
    document.getElementById('toggleBtn').onclick = function() {
      collapsed = !collapsed;
      const box = document.getElementById('outputBox');
      if (collapsed) {
        box.classList.add('collapsed');
        this.textContent = 'Show Output';
      } else {
        box.classList.remove('collapsed');
        this.textContent = 'Hide Output';
      }
    };
    document.getElementById('genBtn').onclick = async function() {
      document.getElementById('genResult').textContent = 'Generating...';
      try {
        const res = await fetch('/generate_traces', { method: 'POST' });
        const data = await res.json();
        document.getElementById('genResult').textContent = data.message;
      } catch (err) {
        document.getElementById('genResult').textContent = 'Error: ' + err;
      }
    };
    document.getElementById('stepBtn').onclick = async function() {
      // Reset simulation before starting
      await fetch('/reset_simulation', { method: 'POST' });
      const fileInput = document.getElementById('traceFile');
      const formData = new FormData();
      if (fileInput.files.length > 0) {
        formData.append('trace', fileInput.files[0]);
      } else {
        const trace = document.getElementById('trace').value;
        formData.append('trace', new Blob([trace]));
      }
      document.getElementById('output').textContent = 'Starting simulation...';
      document.getElementById('outputBox').classList.remove('collapsed');
      document.getElementById('toggleBtn').textContent = 'Hide Output';
      collapsed = false;
      try {
        const res = await fetch('/step_simulate', {
          method: 'POST',
          body: formData
        });
        const data = await res.json();
        updateOutput(data);
        document.getElementById('stepBtn').textContent = 'Step Simulation';
        document.getElementById('nextStepBtn').disabled = false;
        document.getElementById('resetBtn').disabled = false;
      } catch (err) {
        document.getElementById('output').textContent = 'Error: ' + err;
      }
    };
    document.getElementById('nextStepBtn').onclick = async function() {
      try {
        const res = await fetch('/step_simulate', {
          method: 'POST'
        });
        const data = await res.json();
        updateOutput(data);
      } catch (err) {
        document.getElementById('output').textContent = 'Error: ' + err;
      }
    };
    document.getElementById('resetBtn').onclick = async function() {
      try {
        await fetch('/reset_simulation', { method: 'POST' });
        document.getElementById('output').textContent = 'Simulation reset. Click "Start Step Simulation" to begin.';
        document.getElementById('stepBtn').textContent = 'Start Step Simulation';
        document.getElementById('nextStepBtn').disabled = true;
        document.getElementById('resetBtn').disabled = true;
      } catch (err) {
        document.getElementById('output').textContent = 'Error: ' + err;
      }
    };
    function updateOutput(data) {
      const output = document.getElementById('output');
      let html = '';

      // Cycle Information
      html += `
        <div class="cycle-info">
          <span>Cycle: ${data.state.cycle}</span>
          <span>PC: ${data.state.pc}</span>
        </div>
      `;

      // Registers Section
      html += `
        <div class="registers-section">
          <h3>Registers</h3>
          <div class="registers-grid">
      `;
      for (let i = 0; i < data.state.registers.length; i++) {
        const status = data.state.register_status[i] || 'Ready';
        html += `
          <div class="register-item">
            <div class="register-name">R${i}</div>
            <div class="register-value">${data.state.registers[i]}</div>
            <div class="register-status">${status}</div>
          </div>
        `;
      }
      html += `
          </div>
        </div>
      `;

      // Reservation Stations Section
      html += `
        <div class="rs-section">
          <h3>Reservation Stations</h3>
          <div class="rs-grid">
      `;
      data.state.reservation_stations.forEach(rs => {
        html += `
          <div class="rs-item">
            <div class="rs-name">${rs.name}</div>
            <div class="rs-details">
              <span class="rs-label">Operation:</span>
              <span class="rs-value">${rs.op}</span>
              <span class="rs-label">Destination:</span>
              <span class="rs-value">${rs.dest || 'None'}</span>
              <span class="rs-label">Vj:</span>
              <span class="rs-value ${rs.vj === null ? 'waiting' : ''}">${rs.vj !== null ? rs.vj : 'Waiting'}</span>
              <span class="rs-label">Vk:</span>
              <span class="rs-value ${rs.vk === null ? 'waiting' : ''}">${rs.vk !== null ? rs.vk : 'Waiting'}</span>
              <span class="rs-label">Qj:</span>
              <span class="rs-value">${rs.qj || 'None'}</span>
              <span class="rs-label">Qk:</span>
              <span class="rs-value">${rs.qk || 'None'}</span>
              <span class="rs-label">Executing:</span>
              <span class="rs-value">${rs.executing ? 'Yes' : 'No'}</span>
              <span class="rs-label">Cycles Left:</span>
              <span class="rs-value">${rs.cycles_left}</span>
            </div>
          </div>
        `;
      });
      html += `
          </div>
        </div>
      `;

      // CDB Section
      html += `
        <div class="cdb-section">
          <h3>Common Data Bus (CDB)</h3>
      `;
      if (data.state.cdb && data.state.cdb.busy) {
        html += `
          <div class="cdb-active">
            ${data.state.cdb.name} → ${data.state.cdb.value}
          </div>
        `;
      } else {
        html += `
          <div class="cdb-inactive">
            CDB is idle
          </div>
        `;
      }
      html += `</div>`;

      // Simulation Complete Message
      if (!data.continue) {
        html += `
          <div class="simulation-complete">
            Simulation Complete!
          </div>
        `;
      }

      output.innerHTML = html;
    }
    document.getElementById('simForm').onsubmit = async function(e) {
      e.preventDefault();
      const fileInput = document.getElementById('traceFile');
      const formData = new FormData();
      if (fileInput.files.length > 0) {
        formData.append('trace', fileInput.files[0]);
      } else {
        const trace = document.getElementById('trace').value;
        formData.append('trace', new Blob([trace]));
      }
      document.getElementById('output').textContent = 'Simulating...';
      document.getElementById('outputBox').classList.remove('collapsed');
      document.getElementById('toggleBtn').textContent = 'Hide Output';
      collapsed = false;
      try {
        const res = await fetch('/simulate', {
          method: 'POST',
          body: formData
        });
        const data = await res.json();
        const output = document.getElementById('output');
        
        // Parse the report and create a structured output
        const lines = data.report.split('\\n').filter(line => line.trim() !== '');
        let html = '';
        
        // Add metrics section if available
        const metricsMatch = data.report.match(/Total Cycles: (\\d+)\\nTotal Instructions: (\\d+)\\nIPC: ([\\d.]+)/);
        if (metricsMatch) {
          html += `
            <div class="metrics-section">
              <h3>Simulation Metrics</h3>
              <div class="metrics-grid">
                <div class="metric-item">
                  <div class="metric-label">Total Cycles</div>
                  <div class="metric-value">${metricsMatch[1]}</div>
                </div>
                <div class="metric-item">
                  <div class="metric-label">Total Instructions</div>
                  <div class="metric-value">${metricsMatch[2]}</div>
                </div>
                <div class="metric-item">
                  <div class="metric-label">IPC</div>
                  <div class="metric-value">${metricsMatch[3]}</div>
                </div>
              </div>
            </div>
          `;
        }
        
        // Add the rest of the report
        html += '<div class="simulation-report">';
        lines.forEach(line => {
          if (line.startsWith('Cycle')) {
            html += `<div class="cycle-info">${line}</div>`;
          } else if (line.startsWith('Instruction')) {
            html += `<div class="instruction-info">${line}</div>`;
          } else {
            html += `<div>${line}</div>`;
          }
        });
        html += '</div>';
        
        output.innerHTML = html;
      } catch (err) {
        document.getElementById('output').textContent = 'Error: ' + err;
      }
    };
  </script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML)

@app.route('/simulate', methods=['POST'])
def simulate():
    global simulator
    if 'trace' in request.files:
        trace = request.files['trace'].read().decode('utf-8')
    else:
        trace = request.form.get('trace', '')

    with tempfile.NamedTemporaryFile(delete=False, mode='w', suffix='.txt') as f:
        f.write(trace)
        temp_path = f.name

    simulator = Simulator()  # Create new simulator instance
    simulator.load_trace(temp_path)
    report = simulator.run()
    os.remove(temp_path)
    return jsonify({'report': report})

@app.route('/step_simulate', methods=['POST'])
def step_simulate():
    global simulator
    if simulator is None:
        # Initialize simulator if it doesn't exist
        if 'trace' in request.files:
            trace = request.files['trace'].read().decode('utf-8')
        else:
            trace = request.form.get('trace', '')

        with tempfile.NamedTemporaryFile(delete=False, mode='w', suffix='.txt') as f:
            f.write(trace)
            temp_path = f.name

        simulator = Simulator()
        simulator.load_trace(temp_path)
        os.remove(temp_path)

    # Run one step of the simulation
    continue_sim, state = simulator.run_step()
    return jsonify({'continue': continue_sim, 'state': state})

@app.route('/reset_simulation', methods=['POST'])
def reset_simulation():
    global simulator
    simulator = None
    return jsonify({'message': 'Simulation reset'})

@app.route('/generate_traces', methods=['POST'])
def generate_traces():
    try:
        subprocess.run(['python', 'tests/generate_random_traces.py'], check=True)
        return jsonify({'message': 'Random traces generated successfully!'}), 200
    except Exception as e:
        return jsonify({'message': f'Error generating traces: {e}'}), 500

if __name__ == '__main__':
    app.run(debug=True)