"""
Beautiful Classy Results Page
==============================
Matching gradient background, no emojis, professional design

Author: [Nikhitha A]
Date: February 2026
"""

from pathlib import Path

print("\nCreating classy results page...")

app_dir = Path("web_app_integrated")
templates_dir = app_dir / "templates"
templates_dir.mkdir(parents=True, exist_ok=True)

results_html = '''<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Results - Disease Detection</title>
    <style>
        * { 
            margin: 0; 
            padding: 0; 
            box-sizing: border-box; 
        }
        
        body { 
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #a0827d 0%, #d4a89f 50%, #e8c4a0 100%);
            min-height: 100vh;
            padding: 0;
        }
        
        /* Navbar */
        .navbar {
            background: rgba(255, 255, 255, 0.15);
            backdrop-filter: blur(10px);
            padding: 20px 50px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            box-shadow: 0 2px 20px rgba(0,0,0,0.1);
        }
        
        .navbar-left h3 {
            color: white;
            font-size: 1.3em;
            font-weight: 500;
        }
        
        .btn-group {
            display: flex;
            gap: 15px;
        }
        
        .nav-btn {
            padding: 12px 25px;
            border: none;
            border-radius: 10px;
            cursor: pointer;
            font-weight: 600;
            font-size: 1em;
            transition: all 0.3s;
        }
        
        .back-btn {
            background: rgba(255, 255, 255, 0.25);
            backdrop-filter: blur(10px);
            color: white;
            border: 2px solid rgba(255, 255, 255, 0.3);
        }
        
        .back-btn:hover {
            background: rgba(255, 255, 255, 0.35);
            transform: translateY(-2px);
        }
        
        .logout-btn {
            background: linear-gradient(135deg, #e74c3c, #c0392b);
            color: white;
            box-shadow: 0 4px 15px rgba(231, 76, 60, 0.3);
        }
        
        .logout-btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(231, 76, 60, 0.4);
        }
        
        /* Container */
        .container {
            max-width: 1200px;
            margin: 30px auto;
            padding: 0 20px;
        }
        
        /* Consensus Banner */
        .consensus-banner {
            background: rgba(255, 255, 255, 0.4);
            backdrop-filter: blur(15px);
            color: #2c3e50;
            padding: 35px;
            border-radius: 20px;
            text-align: center;
            margin-bottom: 30px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.15);
            border: 2px solid rgba(255, 255, 255, 0.5);
        }
        
        .consensus-banner.partial {
            background: rgba(255, 255, 255, 0.35);
            border: 2px solid rgba(230, 126, 34, 0.3);
        }
        
        .consensus-banner h2 {
            font-size: 1.5em;
            margin-bottom: 10px;
            font-weight: 600;
            color: #27ae60;
        }
        
        .consensus-banner.partial h2 {
            color: #e67e22;
        }
        
        .consensus-banner .disease {
            font-size: 2.5em;
            margin: 15px 0;
            font-weight: 700;
            color: #2c3e50;
        }
        
        .consensus-banner p {
            font-size: 1.1em;
            color: #555;
        }
        
        /* Section Card */
        .section-card {
            background: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(10px);
            border-radius: 20px;
            padding: 35px;
            margin-bottom: 25px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.1);
        }
        
        .section-title {
            font-size: 1.8em;
            color: #2c3e50;
            margin-bottom: 25px;
            padding-bottom: 15px;
            border-bottom: 3px solid #27ae60;
            font-weight: 600;
        }
        
        /* Model Predictions Grid */
        .models-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin-top: 20px;
        }
        
        .model-card {
            background: linear-gradient(135deg, #f8f9fa, #e9ecef);
            padding: 25px;
            border-radius: 15px;
            border-left: 5px solid #27ae60;
            transition: transform 0.2s;
        }
        
        .model-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 8px 25px rgba(0,0,0,0.1);
        }
        
        .model-name {
            font-size: 1.3em;
            font-weight: 700;
            color: #2c3e50;
            margin-bottom: 12px;
        }
        
        .prediction-disease {
            font-size: 1.6em;
            color: #e74c3c;
            font-weight: 700;
            margin: 10px 0;
        }
        
        .prediction-confidence {
            font-size: 1.2em;
            color: #27ae60;
            font-weight: 600;
        }
        
        /* Treatment Section */
        .treatment-section {
            background: rgba(232, 245, 233, 0.95);
            border-radius: 20px;
            padding: 35px;
            margin-bottom: 25px;
            border: 2px solid rgba(39, 174, 96, 0.3);
        }
        
        .subsection-title {
            font-size: 1.5em;
            color: #1b5e20;
            margin: 25px 0 15px 0;
            font-weight: 600;
        }
        
        /* Info Box */
        .info-box {
            background: white;
            padding: 25px;
            border-radius: 15px;
            margin: 20px 0;
            border-left: 5px solid #2196f3;
            box-shadow: 0 3px 15px rgba(0,0,0,0.05);
        }
        
        .info-box h4 {
            color: #1976d2;
            font-size: 1.3em;
            margin-bottom: 15px;
            font-weight: 600;
        }
        
        .info-box p {
            margin: 10px 0;
            line-height: 1.8;
            color: #424242;
            font-size: 1.05em;
        }
        
        .info-box strong {
            color: #1565c0;
        }
        
        /* Treatment Options */
        .treatment-option {
            background: white;
            padding: 25px;
            margin: 15px 0;
            border-radius: 15px;
            border-left: 5px solid #4caf50;
            box-shadow: 0 3px 15px rgba(0,0,0,0.05);
            transition: transform 0.2s;
        }
        
        .treatment-option:hover {
            transform: translateX(10px);
            box-shadow: 0 5px 20px rgba(0,0,0,0.1);
        }
        
        .treatment-option h4 {
            color: #2e7d32;
            font-size: 1.3em;
            margin-bottom: 15px;
            padding-bottom: 10px;
            border-bottom: 2px solid #e8f5e9;
            font-weight: 600;
        }
        
        .treatment-detail {
            margin: 12px 0;
            line-height: 1.8;
            color: #424242;
            font-size: 1.05em;
        }
        
        .treatment-detail strong {
            color: #1b5e20;
            font-weight: 600;
        }
        
        /* Preventive Measures */
        .preventive-box {
            background: #fff3e0;
            padding: 25px;
            border-radius: 15px;
            border-left: 5px solid #ff9800;
            margin: 20px 0;
        }
        
        .preventive-box h4 {
            color: #e65100;
            font-size: 1.3em;
            margin-bottom: 15px;
            font-weight: 600;
        }
        
        .preventive-box ul {
            margin-left: 20px;
        }
        
        .preventive-box li {
            margin: 12px 0;
            line-height: 1.8;
            color: #424242;
            font-size: 1.05em;
        }
        
        /* Cost Comparison */
        .cost-section {
            margin-top: 30px;
        }
        
        .cost-grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 25px;
            margin: 25px 0;
        }
        
        .cost-box {
            padding: 30px;
            border-radius: 20px;
            text-align: center;
            box-shadow: 0 5px 25px rgba(0,0,0,0.1);
            transition: transform 0.3s;
        }
        
        .cost-box:hover {
            transform: scale(1.05);
        }
        
        .cost-organic {
            background: linear-gradient(135deg, #d4edda, #c3e6cb);
            border: 3px solid #28a745;
        }
        
        .cost-chemical {
            background: linear-gradient(135deg, #f8d7da, #f5c6cb);
            border: 3px solid #dc3545;
        }
        
        .cost-box h4 {
            font-size: 1.4em;
            margin-bottom: 15px;
            font-weight: 600;
        }
        
        .cost-box .price {
            font-size: 3em;
            font-weight: 700;
            margin: 20px 0;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.05);
        }
        
        .cost-box .subtitle {
            color: #666;
            font-size: 1em;
            margin-bottom: 15px;
        }
        
        .benefits-list {
            text-align: left;
            margin-top: 15px;
            padding: 15px;
            background: rgba(255,255,255,0.5);
            border-radius: 10px;
        }
        
        .benefits-list div {
            margin: 8px 0;
            font-size: 0.95em;
            color: #2c3e50;
        }
        
        .savings-badge {
            background: linear-gradient(135deg, #28a745, #20c997);
            color: white;
            padding: 20px;
            border-radius: 15px;
            text-align: center;
            font-size: 1.4em;
            font-weight: 700;
            margin-top: 20px;
            box-shadow: 0 5px 20px rgba(40, 167, 69, 0.3);
        }
        
        /* Action Button */
        .action-section {
            text-align: center;
            margin: 40px 0;
        }
        
        .analyze-again-btn {
            background: linear-gradient(135deg, #27ae60, #229954);
            color: white;
            padding: 18px 50px;
            border: none;
            border-radius: 15px;
            font-size: 1.2em;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s;
            box-shadow: 0 5px 20px rgba(39, 174, 96, 0.4);
        }
        
        .analyze-again-btn:hover {
            transform: translateY(-3px);
            box-shadow: 0 8px 25px rgba(39, 174, 96, 0.5);
        }
        
        /* Responsive */
        @media (max-width: 968px) {
            .models-grid,
            .cost-grid {
                grid-template-columns: 1fr;
            }
            
            .navbar {
                padding: 15px 20px;
            }
            
            .btn-group {
                flex-direction: column;
                gap: 10px;
            }
        }
    </style>
</head>
<body>
    <!-- Navbar -->
    <div class="navbar">
        <div class="navbar-left">
            <h3>Analysis Results</h3>
        </div>
        <div class="btn-group">
            <button class="nav-btn back-btn" onclick="window.location.href='/dashboard'">
                ← Back to Dashboard
            </button>
            <button class="nav-btn logout-btn" onclick="window.location.href='/logout'">
                Logout
            </button>
        </div>
    </div>
    
    <div class="container">
        <!-- Consensus Banner -->
        {% if result.consensus.all_agree %}
        <div class="consensus-banner">
            <h2> All Models Agree</h2>
            <div class="disease">{{ result.consensus.majority_disease }}</div>
            <p>All {{ result.consensus.agreement_count }} AI models detected the same disease with high confidence</p>
        </div>
        {% else %}
        <div class="consensus-banner partial">
            <h2> Partial Agreement</h2>
            <div class="disease">{{ result.consensus.majority_disease }}</div>
            <p>{{ result.consensus.agreement_count }} out of {{ result.predictions|length }} models agree</p>
        </div>
        {% endif %}
        
        <!-- Model Predictions -->
        <div class="section-card">
            <h3 class="section-title">Model Predictions</h3>
            <div class="models-grid">
                {% for model_name, pred in result.predictions.items() %}
                <div class="model-card">
                    <div class="model-name">{{ model_name }}</div>
                    <div class="prediction-disease">{{ pred.disease }}</div>
                    <div class="prediction-confidence">Confidence: {{ "%.1f"|format(pred.confidence) }}%</div>
                </div>
                {% endfor %}
            </div>
        </div>
        
        <!-- Treatment Guide -->
        {% if result.treatment %}
        <div class="treatment-section">
            <h3 class="section-title">Treatment & Prevention Guide</h3>
            
            <!-- Disease Information -->
            <div class="info-box">
                <h4>Disease Information</h4>
                <p><strong>Pathogen:</strong> {{ result.treatment.disease_info.pathogen }}</p>
                <p><strong>Symptoms:</strong> {{ result.treatment.disease_info.symptoms }}</p>
                <p><strong>Severity:</strong> {{ result.treatment.disease_info.severity }}</p>
            </div>
            
            <!-- Organic Treatments -->
            <h4 class="subsection-title">Recommended Organic Treatments</h4>
            <p style="color: #2e7d32; margin-bottom: 20px; font-size: 1.05em;">Choose any one of the following effective organic treatments:</p>
            
            {% for treatment in result.treatment.organic_treatments %}
            <div class="treatment-option">
                <h4>Option {{ loop.index }}: {{ treatment.name }}</h4>
                <div class="treatment-detail"><strong>Method:</strong> {{ treatment.method }}</div>
                <div class="treatment-detail"><strong>Dosage:</strong> {{ treatment.dosage }}</div>
                <div class="treatment-detail"><strong>Frequency:</strong> {{ treatment.frequency }}</div>
                <div class="treatment-detail"><strong>Application Time:</strong> {{ treatment.application_time }}</div>
                <div class="treatment-detail"><strong>Effectiveness:</strong> {{ treatment.effectiveness }}</div>
                <div class="treatment-detail"><strong>Cost:</strong> ₹{{ "%.2f"|format(treatment.cost_per_tree) }} per tree</div>
            </div>
            {% endfor %}
            
            <!-- Preventive Measures -->
            <div class="preventive-box">
                <h4>Preventive Measures (Important)</h4>
                <ul>
                    {% for measure in result.treatment.preventive_measures %}
                    <li>{{ measure }}</li>
                    {% endfor %}
                </ul>
            </div>
            
            <!-- Cost Comparison -->
            <div class="cost-section">
                <h4 class="subsection-title" style="text-align: center;">Cost Comparison</h4>
                <div class="cost-grid">
                    <div class="cost-box cost-organic">
                        <h4>Organic Treatment</h4>
                        <div class="price">₹{{ "%.2f"|format(result.treatment.organic_treatments[0].cost_per_tree) }}</div>
                        <div class="subtitle">per tree</div>
                        <div class="benefits-list">
                            <strong style="color: #155724;">Benefits:</strong>
                            <div>✓ Eco-friendly</div>
                            <div>✓ No soil contamination</div>
                            <div>✓ Safe for beneficial insects</div>
                            <div>✓ Sustainable long-term</div>
                        </div>
                    </div>
                    <div class="cost-box cost-chemical">
                        <h4>Chemical Treatment</h4>
                        <div class="price">₹{{ "%.2f"|format(result.treatment.chemical_alternative.cost_per_tree) }}</div>
                        <div class="subtitle">per tree</div>
                        <div class="benefits-list">
                            <strong style="color: #721c24;">Drawbacks:</strong>
                            <div>✗ {{ result.treatment.chemical_alternative.side_effects }}</div>
                            <div>✗ Not recommended</div>
                        </div>
                    </div>
                </div>
                <div class="savings-badge">
                    Save ₹{{ "%.2f"|format(result.treatment.chemical_alternative.cost_per_tree - result.treatment.organic_treatments[0].cost_per_tree) }} per tree with organic treatment
                </div>
            </div>
        </div>
        {% endif %}
        
        <!-- Action Button -->
        <div class="action-section">
            <button class="analyze-again-btn" onclick="window.location.href='/dashboard'">
                ← Analyze Another Image
            </button>
        </div>
    </div>
</body>
</html>
'''

with open(templates_dir / "results.html", "w", encoding='utf-8') as f:
    f.write(results_html)


