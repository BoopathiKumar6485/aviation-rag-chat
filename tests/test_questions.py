"""
50 Test Questions for Aviation RAG System
Based on Sample_test_questions.pdf
"""

# Simple Factual Questions (20)
SIMPLE_QUESTIONS = [
    {
        "question": "What are flight levels referenced to?",
        "type": "simple",
        "expected_source": "Sample_test_questions.pdf",
        "expected_page": 1
    },
    {
        "question": "How many satellites are required by GNSS to determine a 3-D position?",
        "type": "simple",
        "expected_source": "Sample_test_questions.pdf",
        "expected_page": 5
    },
    {
        "question": "What is the capital city of Australia?",
        "type": "simple",
        "expected_source": "Sample_test_questions.pdf",
        "expected_page": 6
    },
    {
        "question": "Who painted the Mona Lisa?",
        "type": "simple",
        "expected_source": "Sample_test_questions.pdf",
        "expected_page": 3
    },
    {
        "question": "What is the primary purpose of aircraft accident investigation?",
        "type": "simple",
        "expected_source": "Sample_test_questions.pdf",
        "expected_page": 11
    },
    {
        "question": "What is the dry adiabatic lapse rate?",
        "type": "simple",
        "expected_source": "Sample_test_questions.pdf",
        "expected_page": 3
    },
    {
        "question": "Which cloud type produces continuous precipitation?",
        "type": "simple",
        "expected_source": "Sample_test_questions.pdf",
        "expected_page": 5
    },
    {
        "question": "What is the largest planet in our solar system?",
        "type": "simple",
        "expected_source": "Sample_test_questions.pdf",
        "expected_page": 5
    },
    {
        "question": "What color are runway threshold lights?",
        "type": "simple",
        "expected_source": "Sample_test_questions.pdf",
        "expected_page": 8
    },
    {
        "question": "Who was the first human to walk on the Moon?",
        "type": "simple",
        "expected_source": "Sample_test_questions.pdf",
        "expected_page": 7
    },
    {
        "question": "What is the primary advantage of SSR over Primary Radar?",
        "type": "simple",
        "expected_source": "Sample_test_questions.pdf",
        "expected_page": 6
    },
    {
        "question": "What does the Certificate of Airworthiness confirm?",
        "type": "simple",
        "expected_source": "Sample_test_questions.pdf",
        "expected_page": 1
    },
    {
        "question": "What is the Point of No Return most sensitive to?",
        "type": "simple",
        "expected_source": "Sample_test_questions.pdf",
        "expected_page": 3
    },
    {
        "question": "Which visibility restriction is caused by hygroscopic particles?",
        "type": "simple",
        "expected_source": "Sample_test_questions.pdf",
        "expected_page": 6
    },
    {
        "question": "What is the RVSM vertical separation between FL290 and FL410?",
        "type": "simple",
        "expected_source": "Sample_test_questions.pdf",
        "expected_page": 9
    },
    {
        "question": "What is the primary objective of Air Traffic Services?",
        "type": "simple",
        "expected_source": "Sample_test_questions.pdf",
        "expected_page": 2
    },
    {
        "question": "How is relative humidity affected by temperature?",
        "type": "simple",
        "expected_source": "Sample_test_questions.pdf",
        "expected_page": 7
    },
    {
        "question": "What is the ISA temperature lapse rate?",
        "type": "simple",
        "expected_source": "Sample_test_questions.pdf",
        "expected_page": 10
    },
    {
        "question": "What does a warm front typically produce?",
        "type": "simple",
        "expected_source": "Sample_test_questions.pdf",
        "expected_page": 11
    },
    {
        "question": "What pressure system is associated with fair weather?",
        "type": "simple",
        "expected_source": "Sample_test_questions.pdf",
        "expected_page": 12
    }
]

# Applied Questions (20)
APPLIED_QUESTIONS = [
    {
        "question": "You are flying at FL350 and need to descend through an inversion layer at constant Mach number. What happens to your CAS and why?",
        "type": "applied",
        "expected_source": "Sample_test_questions.pdf",
        "expected_page": 7
    },
    {
        "question": "During pre-flight planning, you notice the temperature is decreasing with height at 3°C per 1000 ft. Is this stable or unstable conditions? Explain.",
        "type": "applied",
        "expected_source": "Sample_test_questions.pdf",
        "expected_page": 3
    },
    {
        "question": "You are approaching an airport and the visibility is reduced due to haze. What causes this condition and how does it affect your approach?",
        "type": "applied",
        "expected_source": "Sample_test_questions.pdf",
        "expected_page": 6
    },
    {
        "question": "Two aircraft are converging at the same altitude. The other aircraft is on your right. Who gives way?",
        "type": "applied",
        "expected_source": "Sample_test_questions.pdf",
        "expected_page": 2
    },
    {
        "question": "You are flying in Class C airspace. What separation services can you expect as a VFR pilot?",
        "type": "applied",
        "expected_source": "Sample_test_questions.pdf",
        "expected_page": 2
    },
    {
        "question": "During a flight, both pitot and static sources become blocked. What will your ASI indicate?",
        "type": "applied",
        "expected_source": "Sample_test_questions.pdf",
        "expected_page": 1
    },
    {
        "question": "You are planning a long-range flight and need to calculate the Point of No Return. Which factor requires the most accurate forecast?",
        "type": "applied",
        "expected_source": "Sample_test_questions.pdf",
        "expected_page": 6
    },
    {
        "question": "While descending through 10,000 feet, you encounter icing conditions. Which type of ice is most hazardous and why?",
        "type": "applied",
        "expected_source": "Sample_test_questions.pdf",
        "expected_page": 8
    },
    {
        "question": "You are flying near a jet stream and encounter turbulence with no clouds. What is this phenomenon and why does it occur?",
        "type": "applied",
        "expected_source": "Sample_test_questions.pdf",
        "expected_page": 10
    },
    {
        "question": "During approach, you encounter wind shear. Why is this particularly hazardous during take-off and landing?",
        "type": "applied",
        "expected_source": "Sample_test_questions.pdf",
        "expected_page": 11
    },
    {
        "question": "You are flying from low latitude to high latitude using a Mercator chart. How does the scale change and why?",
        "type": "applied",
        "expected_source": "Sample_test_questions.pdf",
        "expected_page": 4
    },
    {
        "question": "A commercial pilot wants to fly for hire. What license requirements apply?",
        "type": "applied",
        "expected_source": "Sample_test_questions.pdf",
        "expected_page": 4
    },
    {
        "question": "You are flying near the coast in the afternoon and encounter a sea breeze. What causes this phenomenon?",
        "type": "applied",
        "expected_source": "Sample_test_questions.pdf",
        "expected_page": 4
    },
    {
        "question": "Your GPS receiver shows a 3D position fix. How many satellites are likely being used?",
        "type": "applied",
        "expected_source": "Sample_test_questions.pdf",
        "expected_page": 5
    },
    {
        "question": "You are flying at FL300 and need to check the latest aeronautical information of long duration. Which document should you consult?",
        "type": "applied",
        "expected_source": "Sample_test_questions.pdf",
        "expected_page": 7
    },
    {
        "question": "During flight, you notice the relative humidity increasing while temperature remains constant. What is happening?",
        "type": "applied",
        "expected_source": "Sample_test_questions.pdf",
        "expected_page": 10
    },
    {
        "question": "You are planning a VFR flight and need to know which airspaces require ATC separation for VFR flights. What classes provide this?",
        "type": "applied",
        "expected_source": "Sample_test_questions.pdf",
        "expected_page": 2
    },
    {
        "question": "During approach, the runway is not visible at 1,000 feet. What action should you take?",
        "type": "applied",
        "expected_source": "Sample_test_questions.pdf",
        "expected_page": 3
    },
    {
        "question": "You are flying in an area with thunderstorms. Which three conditions are necessary for their formation?",
        "type": "applied",
        "expected_source": "Sample_test_questions.pdf",
        "expected_page": 11
    },
    {
        "question": "A NOTAM is issued for your route. What type of information does it contain?",
        "type": "applied",
        "expected_source": "Sample_test_questions.pdf",
        "expected_page": 7
    }
]

# Higher-Order Reasoning Questions (10)
REASONING_QUESTIONS = [
    {
        "question": "Compare and contrast the advantages and disadvantages of SSR versus Primary Radar for approach control in busy airspace. Consider factors like identification, weather penetration, and clutter.",
        "type": "reasoning",
        "expected_source": "Sample_test_questions.pdf",
        "expected_pages": [6, 9]
    },
    {
        "question": "Aircraft A is on approach with both pitot and static sources blocked. Aircraft B has only the static source blocked. How would their ASI indications differ during descent? Explain the aerodynamic principles involved.",
        "type": "reasoning",
        "expected_source": "Sample_test_questions.pdf",
        "expected_page": 1
    },
    {
        "question": "You are flying from the equator to 60°N latitude. Explain how geodetic and geocentric latitude differ and why this matters for navigation systems.",
        "type": "reasoning",
        "expected_source": "Sample_test_questions.pdf",
        "expected_page": 5
    },
    {
        "question": "A front is approaching your position. Based on the cloud types and precipitation patterns, how would you distinguish between a warm front and a cold front? What hazards does each present?",
        "type": "reasoning",
        "expected_source": "Sample_test_questions.pdf",
        "expected_page": 11
    },
    {
        "question": "You are planning a flight that requires RVSM approval. What equipment and certifications are required, and what separation standards apply between FL290 and FL410?",
        "type": "reasoning",
        "expected_source": "Sample_test_questions.pdf",
        "expected_page": 9
    },
    {
        "question": "Explain the relationship between the Certificate of Airworthiness, Certificate of Registration, and Air Operator Certificate. What does each document certify and how do they interact?",
        "type": "reasoning",
        "expected_source": "Sample_test_questions.pdf",
        "expected_pages": [1, 9]
    },
    {
        "question": "During a transoceanic flight, your VHF navigation aids become unreliable. Explain why this occurs and what alternative navigation methods are available.",
        "type": "reasoning",
        "expected_source": "Sample_test_questions.pdf",
        "expected_page": 8
    },
    {
        "question": "Compare the adiabatic processes in rising air parcels with the environmental lapse rate. How does this determine atmospheric stability and cloud formation?",
        "type": "reasoning",
        "expected_source": "Sample_test_questions.pdf",
        "expected_pages": [3, 9]
    },
    {
        "question": "An aircraft must be registered in only one state at a time. Why is this requirement fundamental to international aviation law, and what problems could arise from multiple registrations?",
        "type": "reasoning",
        "expected_source": "Sample_test_questions.pdf",
        "expected_page": 1
    },
    {
        "question": "Explain how the Chicago Convention's objectives influence modern Air Traffic Services. How do these principles affect daily ATC operations?",
        "type": "reasoning",
        "expected_source": "Sample_test_questions.pdf",
        "expected_pages": [6-7]
    }
]

# Combine all questions
ALL_QUESTIONS = SIMPLE_QUESTIONS + APPLIED_QUESTIONS + REASONING_QUESTIONS

# Verify count
print(f"Total questions: {len(ALL_QUESTIONS)}")
print(f"Simple: {len(SIMPLE_QUESTIONS)}")
print(f"Applied: {len(APPLIED_QUESTIONS)}")
print(f"Reasoning: {len(REASONING_QUESTIONS)}")