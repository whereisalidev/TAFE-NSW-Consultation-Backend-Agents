from google.adk.agents import Agent
import os
from dotenv import load_dotenv
from google.adk.models.lite_llm import LiteLlm
from google.adk.tools import FunctionTool


def single_choice_selection__tool():
    html = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Performance Data Assessment</title>
        <style>
            body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                max-width: 100%;
                margin: 0;
                padding: 15px;
                background-color: #f8f9fa;
                line-height: 1.5;
            }
            .consultation-container {
                background: white;
                padding: 25px;
                border-radius: 8px;
                box-shadow: 0 2px 8px rgba(0,0,0,0.08);
                margin-bottom: 20px;
            }
            .intro-text {
                color: #495057;
                margin-bottom: 25px;
                font-size: 16px;
            }
            .question-section {
                margin-bottom: 25px;
                padding: 20px;
                border-left: 4px solid #007bff;
                background-color: #f8f9fa;
                border-radius: 0 6px 6px 0;
            }
            .question-title {
                margin: 0 0 20px 0;
                color: #212529;
                font-size: 18px;
                font-weight: 600;
            }
            .options-container {
                margin-top: 15px;
            }
            .option-item {
                margin: 0;
                padding: 8px 15px;
                border-radius: 6px;
                transition: background-color 0.2s ease;
                cursor: pointer;
            }
            .option-item:hover {
                background-color: #e3f2fd;
            }
            .option-item input[type="radio"] {
                margin-right: 12px;
                accent-color: #007bff;
            }
            .option-item label {
                cursor: pointer;
                color: #495057;
                font-weight: 500;
                font-size: 15px;
            }
        </style>
    </head>
    <body>
        <div class="consultation-container">
            <div class="question-section">
                <h3 class="question-title">How familiar are you with the performance metrics for your area?</h3>
                <div class="options-container">
                    <div class="option-item">
                        <input type="radio" id="very_familiar" name="performance_familiarity" value="Very familiar">
                        <label for="very_familiar">Very familiar</label>
                    </div>
                    <div class="option-item">
                        <input type="radio" id="somewhat_familiar" name="performance_familiarity" value="Somewhat familiar">
                        <label for="somewhat_familiar">Somewhat familiar</label>
                    </div>
                    <div class="option-item">
                        <input type="radio" id="limited_familiarity" name="performance_familiarity" value="Limited familiarity">
                        <label for="limited_familiarity">Limited familiarity</label>
                    </div>
                    <div class="option-item">
                        <input type="radio" id="not_familiar" name="performance_familiarity" value="Not familiar">
                        <label for="not_familiar">Not familiar</label>
                    </div>
                </div>
            </div>
        </div>
    </body>
    </html>
    """
    return {
        "message": html,
        "type": "html"
    }

def rating_scale_tool():
    html = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Current Operational Challenges Assessment</title>
        <style>
            body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                width: 90%;
                margin: 0;
                padding: 15px;
                background-color: #f8f9fa;
                line-height: 1.5;
            }
            .consultation-container {
                background: white;
                padding: 25px;
                border-radius: 8px;
                box-shadow: 0 2px 8px rgba(0,0,0,0.08);
                margin-bottom: 20px;
            }
            .question-section {
                margin-bottom: 25px;
                padding: 20px;
                border-left: 4px solid #007bff;
                background-color: #f8f9fa;
                border-radius: 0 6px 6px 0;
            }
            .question-title {
                margin: 0 0 20px 0;
                color: #212529;
                font-size: 18px;
                font-weight: 600;
            }
            .challenge-item {
                margin-bottom: 20px;
                padding: 15px;
                background-color: white;
                border-radius: 6px;
                border: 1px solid #e9ecef;
            }
            .challenge-label {
                font-weight: 600;
                color: #495057;
                margin-bottom: 10px;
                font-size: 15px;
            }
            .rating-container {
                display: flex;
                justify-content: space-between;
                align-items: center;
                margin-top: 8px;
            }
            .rating-option {
                display: flex;
                flex-direction: column;
                align-items: center;
                margin: 0 5px;
            }
            .rating-option input[type="radio"] {
                margin-bottom: 5px;
                accent-color: #007bff;
                transform: scale(1.2);
            }
            .rating-label {
                font-size: 12px;
                color: #6c757d;
                text-align: center;
                font-weight: 500;
            }
            .scale-labels {
                display: flex;
                justify-content: space-between;
                margin-top: 5px;
                font-size: 11px;
                color: #868e96;
            }
            .submit-container {
                margin-top: 30px;
                text-align: center;
            }
            .submit-btn {
                background-color: #007bff;
                color: white;
                border: none;
                padding: 12px 30px;
                border-radius: 6px;
                font-size: 16px;
                font-weight: 600;
                cursor: pointer;
                transition: background-color 0.2s ease;
            }
            .submit-btn:hover {
                background-color: #0056b3;
            }
            .submit-btn:disabled {
                background-color: #6c757d;
                cursor: not-allowed;
            }
        </style>
    </head>
    <body>
        <div class="consultation-container">
            <div class="question-section">
                <h3 class="question-title">Rate the following challenges in your area (1 = Not a problem, 5 = Major problem):</h3>
                
                <div class="challenge-item">
                    <div class="challenge-label">Staff recruitment/retention</div>
                    <div class="rating-container">
                        <div class="rating-option">
                            <input type="radio" id="staff_1" name="staff_recruitment" value="1">
                            <label for="staff_1" class="rating-label">1</label>
                        </div>
                        <div class="rating-option">
                            <input type="radio" id="staff_2" name="staff_recruitment" value="2">
                            <label for="staff_2" class="rating-label">2</label>
                        </div>
                        <div class="rating-option">
                            <input type="radio" id="staff_3" name="staff_recruitment" value="3">
                            <label for="staff_3" class="rating-label">3</label>
                        </div>
                        <div class="rating-option">
                            <input type="radio" id="staff_4" name="staff_recruitment" value="4">
                            <label for="staff_4" class="rating-label">4</label>
                        </div>
                        <div class="rating-option">
                            <input type="radio" id="staff_5" name="staff_recruitment" value="5">
                            <label for="staff_5" class="rating-label">5</label>
                        </div>
                    </div>
                    <div class="scale-labels">
                        <span>Not a problem</span>
                        <span>Major problem</span>
                    </div>
                </div>

                <div class="challenge-item">
                    <div class="challenge-label">Student recruitment/retention</div>
                    <div class="rating-container">
                        <div class="rating-option">
                            <input type="radio" id="student_1" name="student_recruitment" value="1">
                            <label for="student_1" class="rating-label">1</label>
                        </div>
                        <div class="rating-option">
                            <input type="radio" id="student_2" name="student_recruitment" value="2">
                            <label for="student_2" class="rating-label">2</label>
                        </div>
                        <div class="rating-option">
                            <input type="radio" id="student_3" name="student_recruitment" value="3">
                            <label for="student_3" class="rating-label">3</label>
                        </div>
                        <div class="rating-option">
                            <input type="radio" id="student_4" name="student_recruitment" value="4">
                            <label for="student_4" class="rating-label">4</label>
                        </div>
                        <div class="rating-option">
                            <input type="radio" id="student_5" name="student_recruitment" value="5">
                            <label for="student_5" class="rating-label">5</label>
                        </div>
                    </div>
                    <div class="scale-labels">
                        <span>Not a problem</span>
                        <span>Major problem</span>
                    </div>
                </div>

                <div class="challenge-item">
                    <div class="challenge-label">Industry placement capacity</div>
                    <div class="rating-container">
                        <div class="rating-option">
                            <input type="radio" id="industry_1" name="industry_placement" value="1">
                            <label for="industry_1" class="rating-label">1</label>
                        </div>
                        <div class="rating-option">
                            <input type="radio" id="industry_2" name="industry_placement" value="2">
                            <label for="industry_2" class="rating-label">2</label>
                        </div>
                        <div class="rating-option">
                            <input type="radio" id="industry_3" name="industry_placement" value="3">
                            <label for="industry_3" class="rating-label">3</label>
                        </div>
                        <div class="rating-option">
                            <input type="radio" id="industry_4" name="industry_placement" value="4">
                            <label for="industry_4" class="rating-label">4</label>
                        </div>
                        <div class="rating-option">
                            <input type="radio" id="industry_5" name="industry_placement" value="5">
                            <label for="industry_5" class="rating-label">5</label>
                        </div>
                    </div>
                    <div class="scale-labels">
                        <span>Not a problem</span>
                        <span>Major problem</span>
                    </div>
                </div>

                <div class="challenge-item">
                    <div class="challenge-label">Equipment/technology adequacy</div>
                    <div class="rating-container">
                        <div class="rating-option">
                            <input type="radio" id="equipment_1" name="equipment_technology" value="1">
                            <label for="equipment_1" class="rating-label">1</label>
                        </div>
                        <div class="rating-option">
                            <input type="radio" id="equipment_2" name="equipment_technology" value="2">
                            <label for="equipment_2" class="rating-label">2</label>
                        </div>
                        <div class="rating-option">
                            <input type="radio" id="equipment_3" name="equipment_technology" value="3">
                            <label for="equipment_3" class="rating-label">3</label>
                        </div>
                        <div class="rating-option">
                            <input type="radio" id="equipment_4" name="equipment_technology" value="4">
                            <label for="equipment_4" class="rating-label">4</label>
                        </div>
                        <div class="rating-option">
                            <input type="radio" id="equipment_5" name="equipment_technology" value="5">
                            <label for="equipment_5" class="rating-label">5</label>
                        </div>
                    </div>
                    <div class="scale-labels">
                        <span>Not a problem</span>
                        <span>Major problem</span>
                    </div>
                </div>

                <div class="challenge-item">
                    <div class="challenge-label">Facility capacity/condition</div>
                    <div class="rating-container">
                        <div class="rating-option">
                            <input type="radio" id="facility_1" name="facility_capacity" value="1">
                            <label for="facility_1" class="rating-label">1</label>
                        </div>
                        <div class="rating-option">
                            <input type="radio" id="facility_2" name="facility_capacity" value="2">
                            <label for="facility_2" class="rating-label">2</label>
                        </div>
                        <div class="rating-option">
                            <input type="radio" id="facility_3" name="facility_capacity" value="3">
                            <label for="facility_3" class="rating-label">3</label>
                        </div>
                        <div class="rating-option">
                            <input type="radio" id="facility_4" name="facility_capacity" value="4">
                            <label for="facility_4" class="rating-label">4</label>
                        </div>
                        <div class="rating-option">
                            <input type="radio" id="facility_5" name="facility_capacity" value="5">
                            <label for="facility_5" class="rating-label">5</label>
                        </div>
                    </div>
                    <div class="scale-labels">
                        <span>Not a problem</span>
                        <span>Major problem</span>
                    </div>
                </div>

                <div class="challenge-item">
                    <div class="challenge-label">Curriculum relevance</div>
                    <div class="rating-container">
                        <div class="rating-option">
                            <input type="radio" id="curriculum_1" name="curriculum_relevance" value="1">
                            <label for="curriculum_1" class="rating-label">1</label>
                        </div>
                        <div class="rating-option">
                            <input type="radio" id="curriculum_2" name="curriculum_relevance" value="2">
                            <label for="curriculum_2" class="rating-label">2</label>
                        </div>
                        <div class="rating-option">
                            <input type="radio" id="curriculum_3" name="curriculum_relevance" value="3">
                            <label for="curriculum_3" class="rating-label">3</label>
                        </div>
                        <div class="rating-option">
                            <input type="radio" id="curriculum_4" name="curriculum_relevance" value="4">
                            <label for="curriculum_4" class="rating-label">4</label>
                        </div>
                        <div class="rating-option">
                            <input type="radio" id="curriculum_5" name="curriculum_relevance" value="5">
                            <label for="curriculum_5" class="rating-label">5</label>
                        </div>
                    </div>
                    <div class="scale-labels">
                        <span>Not a problem</span>
                        <span>Major problem</span>
                    </div>
                </div>

                <div class="challenge-item">
                    <div class="challenge-label">Regulatory compliance</div>
                    <div class="rating-container">
                        <div class="rating-option">
                            <input type="radio" id="regulatory_1" name="regulatory_compliance" value="1">
                            <label for="regulatory_1" class="rating-label">1</label>
                        </div>
                        <div class="rating-option">
                            <input type="radio" id="regulatory_2" name="regulatory_compliance" value="2">
                            <label for="regulatory_2" class="rating-label">2</label>
                        </div>
                        <div class="rating-option">
                            <input type="radio" id="regulatory_3" name="regulatory_compliance" value="3">
                            <label for="regulatory_3" class="rating-label">3</label>
                        </div>
                        <div class="rating-option">
                            <input type="radio" id="regulatory_4" name="regulatory_compliance" value="4">
                            <label for="regulatory_4" class="rating-label">4</label>
                        </div>
                        <div class="rating-option">
                            <input type="radio" id="regulatory_5" name="regulatory_compliance" value="5">
                            <label for="regulatory_5" class="rating-label">5</label>
                        </div>
                    </div>
                    <div class="scale-labels">
                        <span>Not a problem</span>
                        <span>Major problem</span>
                    </div>
                </div>

                <div class="challenge-item">
                    <div class="challenge-label">Funding/budget constraints</div>
                    <div class="rating-container">
                        <div class="rating-option">
                            <input type="radio" id="funding_1" name="funding_budget" value="1">
                            <label for="funding_1" class="rating-label">1</label>
                        </div>
                        <div class="rating-option">
                            <input type="radio" id="funding_2" name="funding_budget" value="2">
                            <label for="funding_2" class="rating-label">2</label>
                        </div>
                        <div class="rating-option">
                            <input type="radio" id="funding_3" name="funding_budget" value="3">
                            <label for="funding_3" class="rating-label">3</label>
                        </div>
                        <div class="rating-option">
                            <input type="radio" id="funding_4" name="funding_budget" value="4">
                            <label for="funding_4" class="rating-label">4</label>
                        </div>
                        <div class="rating-option">
                            <input type="radio" id="funding_5" name="funding_budget" value="5">
                            <label for="funding_5" class="rating-label">5</label>
                        </div>
                    </div>
                    <div class="scale-labels">
                        <span>Not a problem</span>
                        <span>Major problem</span>
                    </div>
                </div>

                <div class="challenge-item">
                    <div class="challenge-label">Industry partnerships</div>
                    <div class="rating-container">
                        <div class="rating-option">
                            <input type="radio" id="partnerships_1" name="industry_partnerships" value="1">
                            <label for="partnerships_1" class="rating-label">1</label>
                        </div>
                        <div class="rating-option">
                            <input type="radio" id="partnerships_2" name="industry_partnerships" value="2">
                            <label for="partnerships_2" class="rating-label">2</label>
                        </div>
                        <div class="rating-option">
                            <input type="radio" id="partnerships_3" name="industry_partnerships" value="3">
                            <label for="partnerships_3" class="rating-label">3</label>
                        </div>
                        <div class="rating-option">
                            <input type="radio" id="partnerships_4" name="industry_partnerships" value="4">
                            <label for="partnerships_4" class="rating-label">4</label>
                        </div>
                        <div class="rating-option">
                            <input type="radio" id="partnerships_5" name="industry_partnerships" value="5">
                            <label for="partnerships_5" class="rating-label">5</label>
                        </div>
                    </div>
                    <div class="scale-labels">
                        <span>Not a problem</span>
                        <span>Major problem</span>
                    </div>
                </div>

                <div class="challenge-item">
                    <div class="challenge-label">Student support services</div>
                    <div class="rating-container">
                        <div class="rating-option">
                            <input type="radio" id="support_1" name="student_support" value="1">
                            <label for="support_1" class="rating-label">1</label>
                        </div>
                        <div class="rating-option">
                            <input type="radio" id="support_2" name="student_support" value="2">
                            <label for="support_2" class="rating-label">2</label>
                        </div>
                        <div class="rating-option">
                            <input type="radio" id="support_3" name="student_support" value="3">
                            <label for="support_3" class="rating-label">3</label>
                        </div>
                        <div class="rating-option">
                            <input type="radio" id="support_4" name="student_support" value="4">
                            <label for="support_4" class="rating-label">4</label>
                        </div>
                        <div class="rating-option">
                            <input type="radio" id="support_5" name="student_support" value="5">
                            <label for="support_5" class="rating-label">5</label>
                        </div>
                    </div>
                    <div class="scale-labels">
                        <span>Not a problem</span>
                        <span>Major problem</span>
                    </div>
                </div>

                <div class="submit-container">
                    <button type="button" class="submit-btn" id="submit-ratings">Submit Ratings</button>
                </div>
            </div>
        </div>

        <script>
            document.addEventListener('DOMContentLoaded', function() {
                const submitBtn = document.getElementById('submit-ratings');
                const radioGroups = [
                    'staff_recruitment', 'student_recruitment', 'industry_placement', 
                    'equipment_technology', 'facility_capacity', 'curriculum_relevance',
                    'regulatory_compliance', 'funding_budget', 'industry_partnerships', 'student_support'
                ];

                function checkAllSelected() {
                    const allSelected = radioGroups.every(group => 
                        document.querySelector(`input[name="${group}"]:checked`)
                    );
                    submitBtn.disabled = !allSelected;
                }

                // Add event listeners to all radio buttons
                radioGroups.forEach(group => {
                    const radios = document.querySelectorAll(`input[name="${group}"]`);
                    radios.forEach(radio => {
                        radio.addEventListener('change', checkAllSelected);
                    });
                });

                // Initial check
                checkAllSelected();

                submitBtn.addEventListener('click', function() {
                    const ratings = {};
                    radioGroups.forEach(group => {
                        const selected = document.querySelector(`input[name="${group}"]:checked`);
                        if (selected) {
                            ratings[group] = selected.value;
                        }
                    });

                    // Create a formatted response message
                    const challengeLabels = {
                        'staff_recruitment': 'Staff recruitment/retention',
                        'student_recruitment': 'Student recruitment/retention', 
                        'industry_placement': 'Industry placement capacity',
                        'equipment_technology': 'Equipment/technology adequacy',
                        'facility_capacity': 'Facility capacity/condition',
                        'curriculum_relevance': 'Curriculum relevance',
                        'regulatory_compliance': 'Regulatory compliance',
                        'funding_budget': 'Funding/budget constraints',
                        'industry_partnerships': 'Industry partnerships',
                        'student_support': 'Student support services'
                    };

                    let responseMessage = "Here are my ratings for the operational challenges:\\n\\n";
                    Object.entries(ratings).forEach(([key, value]) => {
                        responseMessage += `${challengeLabels[key]}: ${value}/5\\n`;
                    });

                    // Trigger the response mechanism
                    if (window.parent && window.parent.handleRatingSubmission) {
                        window.parent.handleRatingSubmission(responseMessage);
                    } else {
                        // Fallback for direct integration
                        alert('Ratings submitted: ' + responseMessage);
                    }
                });
            });
        </script>
    </body>
    </html>
    """
    return {
        "message": html,
        "type": "html"
    }

def rating_scale_v2_tool():
    html = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Priority Areas for Investment</title>
    <style>
        body {
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        width: 90%;
        margin: 0;
        padding: 15px;
        background-color: #f8f9fa;
        line-height: 1.5;
        }
        .consultation-container {
        background: white;
        padding: 25px;
        border-radius: 8px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
        margin-bottom: 20px;
        }
        .question-section {
        margin-bottom: 25px;
        padding: 20px;
        border-left: 4px solid #007bff;
        background-color: #f8f9fa;
        border-radius: 0 6px 6px 0;
        }
        .question-title {
        margin: 0 0 20px 0;
        color: #212529;
        font-size: 18px;
        font-weight: 600;
        }
        .challenge-item {
        margin-bottom: 20px;
        padding: 15px;
        background-color: white;
        border-radius: 6px;
        border: 1px solid #e9ecef;
        }
        .challenge-label {
        font-weight: 600;
        color: #495057;
        margin-bottom: 10px;
        font-size: 15px;
        }
        .rating-container {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-top: 8px;
        }
        .rating-option {
        display: flex;
        flex-direction: column;
        align-items: center;
        margin: 0 5px;
        }
        .rating-option input[type="radio"] {
        margin-bottom: 5px;
        accent-color: #007bff;
        transform: scale(1.2);
        }
        .rating-label {
        font-size: 12px;
        color: #6c757d;
        text-align: center;
        font-weight: 500;
        }
        .scale-labels {
        display: flex;
        justify-content: space-between;
        margin-top: 5px;
        font-size: 11px;
        color: #868e96;
        }
        .submit-container {
        margin-top: 30px;
        text-align: center;
        }
        .submit-btn {
        background-color: #007bff;
        color: white;
        border: none;
        padding: 12px 30px;
        border-radius: 6px;
        font-size: 16px;
        font-weight: 600;
        cursor: pointer;
        transition: background-color 0.2s ease;
        }
        .submit-btn:hover {
        background-color: #0056b3;
        }
        .submit-btn:disabled {
        background-color: #6c757d;
        cursor: not-allowed;
        }
    </style>
    </head>
    <body>
    <div class="consultation-container">
        <div class="question-section">
        <h3 class="question-title">If you had additional resources, rank your top 5 investment priorities (1 = highest priority):</h3>
        <div id="challenge-list"></div>

        <div class="submit-container">
            <button type="button" class="submit-btn" id="submit-ratings">Submit Ratings</button>
        </div>
        </div>
    </div>

    <script>
        const challenges = [
        { key: "additional_staff", label: "Additional teaching staff" },
        { key: "professional_development", label: "Professional development for existing staff" },
        { key: "new_equipment", label: "New/upgraded equipment" },
        { key: "facility_improvements", label: "Facility improvements/expansion" },
        { key: "technology_infrastructure", label: "Technology infrastructure" },
        { key: "industry_partnership_development", label: "Industry partnership development" },
        { key: "marketing", label: "Marketing/student recruitment" },
        { key: "curriculum_development", label: "Curriculum development/refresh" },
        { key: "assessment_development", label: "Assessment development/refresh" },
        { key: "quality_assurance", label: "Quality assurance/compliance systems" },
        { key: "research_innovation", label: "Research and innovation capabilities" }
        ];

        const container = document.getElementById("challenge-list");

        // Generate challenge items dynamically
        challenges.forEach(challenge => {
        const item = document.createElement("div");
        item.className = "challenge-item";

        item.innerHTML = `
            <div class="challenge-label">${challenge.label}</div>
            <div class="rating-container">
            ${[1,2,3,4,5].map(num => `
                <div class="rating-option">
                <input type="radio" id="${challenge.key}_${num}" name="${challenge.key}" value="${num}">
                <label for="${challenge.key}_${num}" class="rating-label">${num}</label>
                </div>
            `).join("")}
            </div>
            <div class="scale-labels"><span>Highest Priority</span><span>Lowest Priority</span></div>
        `;

        container.appendChild(item);
        });

        // Submission handling
        const submitBtn = document.getElementById('submit-ratings');
        function checkAllSelected() {
        const allSelected = challenges.every(c => document.querySelector(`input[name="${c.key}"]:checked`));
        submitBtn.disabled = !allSelected;
        }

        document.addEventListener("change", checkAllSelected);

        submitBtn.addEventListener("click", () => {
        const ratings = {};
        challenges.forEach(c => {
            const selected = document.querySelector(`input[name="${c.key}"]:checked`);
            ratings[c.label] = selected ? selected.value : "Not selected";
        });

        let responseMessage = "Here are my ratings:\n\n";
        Object.entries(ratings).forEach(([label, value]) => {
            responseMessage += `${label}: ${value}/5\n`;
        });

        alert(responseMessage);
        });

        // Initial state
        checkAllSelected();
    </script>
    </body>
    </html>

    """
    return {
        "message": html,
        "type": "html"
    }


root_agent = Agent(
    name="riley_strategic_consultant",
    description="Riley - A strategic consultant AI specialized in priority discovery and strategic planning for TAFE NSW departments.",
    instruction="""
    You are Riley, an experienced strategic consultant specializing in priority discovery and strategic planning for TAFE NSW departments.

    CORE IDENTITY:
    - Warm, strategic thinker with future-focused approach
    - Expert in education sector, particularly VET and TAFE NSW structure
    - Uses collaborative communication style with structured information gathering
    - Speaks in Australian English with professional yet approachable tone

    EXPERTISE AREAS:
    - Strategic planning methodologies (SWOT, Balanced Scorecard, OKRs)
    - Priority frameworks (Eisenhower Matrix, MoSCoW)
    - TAFE NSW structure, faculty hierarchies, and strategic direction
    - VET sector challenges and industry partnerships
    - Change management and stakeholder analysis
    - Resource allocation and performance measurement

    STRUCTURED CONSULTATION PROCESS:
    Follow this exact sequence to gather stakeholder context:

    SECTION 1: STAKEHOLDER CONTEXT
    1.1 Basic Information (ALREADY PROVIDED)
    The user's name, position/role, and department are already provided from the frontend registration.

    1.2 Role Context
    Start with: "G'day [name]! I'm Riley, your strategic consultant. I can see you're working as [position] in [department]. To provide you with the best strategic support, I'd like to understand your experience and working relationships better. Let's start with your background:"

    Ask ONE question at a time in this EXACT order:
    1. "How many years have you been in your current position?"
    2. "How long have you been with TAFE NSW overall?"
    3. "Do you have any direct reports? If so, how many?"
    4. "Who are the key internal stakeholders you work with most regularly?"
    5. "What about external stakeholders - who do you collaborate with outside TAFE NSW?"

    CRITICAL: After question 4 about internal stakeholders, you MUST ask question 5 about external stakeholders. Do NOT proceed to SECTION 2 until all questions in SECTION 1.2 are answered.

    SECTION 2: CURRENT STATE ASSESSMENT
    2.1 Performance Data Review
    ONLY after completing ALL 5 role context questions in SECTION 1.2, call the single_choice_selection__tool. The *ONLY* thing you should return is the *EXACT* HTML in "message" from tool response, without any curly braces, provided by the tool, *without any surrounding text or tags*. Do *NOT* include any introductory phrases or explanations. Just the HTML. After the user responds about performance data familiarity, then ask: "What additional data would be most helpful for you in your role?"

    2.2 Current Operational Challenges
    ONLY after completing the performance data questions in SECTION 2.1, call the rating_scale_tool. The *ONLY* thing you should return is the *EXACT* HTML in "message" from tool response, without any curly braces, provided by the tool, *without any surrounding text or tags*. Do *NOT* include any introductory phrases or explanations. Just the HTML.

    2.3 Biggest Operational Pain Points
    What are the top 3 operational challenges keeping you awake at night?

    SECTION 3: Strategic Priorities 
    3.1 Strategic Vision
    In your ideal world, what would your discipline/teaching area/programs look like in 3-5 years?

    3.2 Priority Areas for Investment
    ONLY after completing the SECTION 3.1, call the rating_scale_v2_tool. The *ONLY* thing you should return is the *EXACT* HTML in "message" from tool response, without any curly braces, provided by the tool, *without any surrounding text or tags*. Do *NOT* include any introductory phrases or explanations. Just the HTML.

    CONVERSATION FLOW:
    1. Start with personalized greeting using their actual name
    2. Ask ONE role context question per response (5 questions total)
    3. Ask about performance data familiarity using the HTML format above
    4. Ask about additional data needs
    5. Once all context is gathered, proceed to strategic consultation

    RESPONSE GUIDELINES:
    - Keep responses focused and structured
    - Ask ONE question per response to maintain flow and engagement
    - Be systematic but conversational
    - Don't proceed to strategic consultation until all context is gathered
    - Use Australian spelling and terminology
    - For regular conversation: Use paragraphs with proper spacing
    - For interactive questions: Use the exact HTML format provided above

    PROGRESSION RULES:
    - Do NOT ask about strategic challenges until ALL stakeholder context is complete
    - Complete Section 1.2 before moving to Section 2.1
    - NEVER skip questions or jump to analysis before all context is gathered

    CRITICAL SEQUENCE CONTROL:
    - After internal stakeholders question, ALWAYS ask about external stakeholders next
    - After external stakeholders question, ALWAYS ask about performance data familiarity using HTML format
    - Do NOT provide strategic analysis until ALL context questions are answered

    IMPORTANT: Follow the structured sequence exactly. Do not skip sections or ask strategic questions until the full stakeholder context assessment is complete.

    Your goal is to systematically gather stakeholder context before proceeding to strategic consultation and priority discovery.
    """,
    model=LiteLlm("gemini/gemini-2.5-flash"),
    tools=[FunctionTool(single_choice_selection__tool), FunctionTool(rating_scale_tool), FunctionTool(rating_scale_v2_tool)]
)
