"""
Task Manager for the Strategic Consultant Agent.
Handles consultation sessions and priority analysis.
"""

import os
import logging
import uuid
from typing import Dict, Any, Optional, List

from google.adk.agents import Agent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.adk.artifacts.in_memory_artifact_service import InMemoryArtifactService
from google.genai import types as adk_types

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Define app name for the runner
A2A_APP_NAME = "strategic_consultant_app"

class TaskManager:
    """Task Manager for the Strategic Consultant Agent."""
    
    def __init__(self, agent: Agent):
        """Initialize with an Agent instance and set up ADK Runner."""
        logger.info(f"Initializing TaskManager for agent: {agent.name}")
        self.agent = agent
        
        # Initialize ADK services
        self.session_service = InMemorySessionService()
        self.artifact_service = InMemoryArtifactService()
        
        # Create the runner
        self.runner = Runner(
            agent=self.agent,
            app_name=A2A_APP_NAME,
            session_service=self.session_service,
            artifact_service=self.artifact_service
        )
        logger.info(f"ADK Runner initialized for app '{self.runner.app_name}'")

    async def process_task(self, message: str, context: Dict[str, Any] = None, session_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Process a strategic consultation request.
        
        Args:
            message: The user's message
            context: Context containing user_id, department info, etc.
            session_id: Session identifier
            
        Returns:
            Response dict with message and status
        """
        try:
            # Extract context information
            if not context:
                context = {}
            
            user_id = context.get("user_id", "default_user")
            department = context.get("department", "Unknown Department")
            conversation_history = context.get("conversationHistory", []) # Same key as first file

            # Build comprehensive system instruction using Riley's context
            system_instruction = self._build_riley_context(
                current_message=message, 
                context=context, 
                department=department, 
                conversation_history=conversation_history
            )
            
            # Create or generate session
            if not session_id:
                session_id = str(uuid.uuid4())
            
            # Create session
            try:
                await self.session_service.create_session(
                    app_name=A2A_APP_NAME,
                    user_id=user_id,
                    session_id=session_id,
                    state={}
                )
            except Exception as e:
                logger.warning(f"Session creation issue: {e}")
            
            # Create user message with comprehensive system instruction
            # The system_instruction now includes the conversation history and current user message
            request_content = adk_types.Content(
                role="user", # The ADK runner expects the new message to be from the user
                parts=[adk_types.Part(text=system_instruction)]
            )
            
            # Run the agent with the new message
            events_async = self.runner.run_async(
                user_id=user_id,
                session_id=session_id,
                new_message=request_content # Pass the single new message
            )
            
            # Process response
            final_message = "Hello! I'm Riley, your strategic consultant. How can I help you today?"
            
            async for event in events_async:
                if event.is_final_response() and event.content and event.content.role == "model":
                    if event.content.parts and event.content.parts[0].text:
                        final_message = event.content.parts[0].text
                        logger.info(f"Agent response: {final_message}")
            
            # Handle special cases like analysis completion (same as first file)
            response_result = await self._handle_special_responses(
                final_message, message, context, user_id
            )
            
            if response_result:
                return response_result
            
            return {
                "message": final_message,
                "status": "success",
                "session_id": session_id,
                "data": {
                    "conversation_stage": self._analyze_conversation_context(message, conversation_history),
                    "department": department
                }
            }
            
        except Exception as e:
            logger.error(f"Error processing task: {e}")
            return {
                "message": f"I apologize, but I encountered an error while processing your request: {str(e)}",
                "status": "error"
            }
    
    def _build_riley_context(self, current_message: str, context: Dict, department: str, conversation_history: List[Dict]) -> str:
        """Build comprehensive context for Riley's response."""
        
        # Analyze conversation stage and user needs
        conversation_stage = self._analyze_conversation_context(current_message, conversation_history)
        strategic_focus = self._identify_strategic_focus(current_message, conversation_history)
        
        # Format conversation history
        formatted_history = self._format_conversation_history(conversation_history)
        
        # Get Riley's strategic questioning approach
        questioning_strategy = self._get_strategic_questioning_approach(conversation_stage, strategic_focus)
        
        # Add progression trigger
        progression_guidance = ""
        if conversation_stage == "analysis_phase":
            progression_guidance = """
    
CRITICAL: Riley must now STOP asking questions and START ANALYSIS. Say something like:
"Based on our conversation, I can see several strategic priorities emerging. Let me provide you with my analysis..."

Then provide:
1. Summary of priorities discussed
2. Strategic analysis with scores (Importance/Urgency out of 10)
3. Categorization by themes
4. Recommendations for next steps
"""
        elif len(conversation_history) >= 8:  # Force progression after 8 messages
            progression_guidance = """
    
CRITICAL: Too many questions asked. Riley must now CONCLUDE the discovery phase and provide STRATEGIC ANALYSIS and ACTION RECOMMENDATIONS. Do not ask more questions.
"""

        return f"""
RILEY'S CONSULTATION CONTEXT:

CURRENT SITUATION:
- Department: {department}
- User ID: {context.get('user_id', 'unknown')}
- Conversation Stage: {conversation_stage}
- Strategic Focus Area: {strategic_focus}

CONVERSATION HISTORY:
{formatted_history}

RILEY'S STRATEGIC APPROACH FOR THIS RESPONSE:
{questioning_strategy}

TAFE NSW CONTEXT TO CONSIDER:
- TAFE NSW is Australia's largest vocational education provider
- Focus on industry-relevant training and student outcomes
- Strategic priorities include digital transformation, industry partnerships, and future skills
- Operates across multiple faculties with diverse departmental needs
- Subject to ASQA requirements and government policy frameworks

RILEY'S RESPONSE GUIDELINES:
1. Acknowledge what the user has shared
2. Use strategic thinking to identify underlying priorities
3. Ask 1 probing question on each response that help uncover strategic insights
4. Reference TAFE NSW context when relevant
5. Keep response conversational but professionally focused
6. Build on previous conversation threads
7. Challenge assumptions constructively when appropriate

Remember: You are Riley having a strategic conversation. Be warm, curious, and genuinely interested in helping them discover their priorities.

CURRENT USER MESSAGE: "{current_message}"

Respond as Riley would in this consultation context:

{progression_guidance}
"""
    
    # Replace the _analyze_conversation_context method in your task_manager.py:

    def _analyze_conversation_context(self, current_message: str, history: List[Dict]) -> str:
        """Analyze the conversation to determine current stage."""
        
        message_lower = current_message.lower()
        history_length = len(history)
        
        # Initialize last_ai_message outside the if block
        last_ai_message = ""
        
        # Check if consultation is complete based on previous messages
        if history_length > 0:
            for msg in reversed(history):
                if msg.get('sender') == 'ai':
                    last_ai_message = msg.get('message', '').lower()
                    break
            
            # If the last AI message contained analysis/action plan and user is saying thanks/goodbye
            if (any(phrase in last_ai_message for phrase in ["action plan", "strategic analysis", "recommendations for next steps", "pleasure helping"]) 
                and any(phrase in message_lower for phrase in ["thanks", "thank you", "bye", "goodbye", "see you", "great", "perfect", "excellent"])):
                return "consultation_complete"

        # Count substantive exchanges (not just greetings)
        substantive_exchanges = len([h for h in history if len(h.get('message', '')) > 20])
        
        if history_length == 0 or any(keyword in message_lower for keyword in ["hello", "hi", "start", "begin"]):
            return "initial_engagement"
        elif substantive_exchanges < 2:
            return "context_gathering"
        elif substantive_exchanges < 4 and any(keyword in message_lower for keyword in ["challenge", "problem", "issue", "difficulty"]):
            return "problem_identification"
        elif substantive_exchanges < 6:
            return "priority_discovery"
        elif substantive_exchanges >= 6 and not any(keyword in message_lower for keyword in ["analysis", "summary", "plan"]):
            return "analysis_phase"  # Force analysis after 6 exchanges
        elif any(keyword in message_lower for keyword in ["action", "implement", "next steps", "plan"]):
            return "action_planning"
        else:
            return "analysis_phase"  # Default to analysis if too many exchanges
            
    def _identify_strategic_focus(self, current_message: str, history: List[Dict]) -> str:
        """Identify the strategic focus area from the conversation."""
        
        combined_text = current_message.lower()
        if history:
            combined_text += " " + " ".join([msg.get('message', '').lower() for msg in history[-3:]])
        
        if any(keyword in combined_text for keyword in ["student", "learner", "enrollment", "completion"]):
            return "student_outcomes"
        elif any(keyword in combined_text for keyword in ["industry", "employer", "partnership", "workplace"]):
            return "industry_engagement"
        elif any(keyword in combined_text for keyword in ["digital", "technology", "online", "system"]):
            return "digital_transformation"
        elif any(keyword in combined_text for keyword in ["staff", "teacher", "faculty", "workforce"]):
            return "workforce_development"
        elif any(keyword in combined_text for keyword in ["quality", "compliance", "asqa", "standard"]):
            return "quality_assurance"
        elif any(keyword in combined_text for keyword in ["budget", "resource", "funding", "cost"]):
            return "resource_management"
        else:
            return "strategic_planning"
    
    def _get_strategic_questioning_approach(self, stage: str, focus: str) -> str:
        """Get Riley's strategic questioning approach based on context."""
        
        stage_approaches = {
            "initial_engagement": """
            Riley should:
            - Welcome them warmly and establish rapport
            - Ask "What are the top 3 things keeping you awake at night about your department?"
            - Set the consultation tone as collaborative and strategic
            """,
            "context_gathering": """
            Riley should:
            - Build understanding of their department's current situation
            - Ask about their role, team, and main responsibilities
            - After 2-3 exchanges, move to problem identification
            """,
            "problem_identification": """
            Riley should:
            - Dive deeper into challenges they've mentioned
            - Ask "What's driving this - is it student outcomes, industry demand, or regulatory requirements?"
            - After identifying 2-3 key challenges, move to priority discovery
            """,
            "priority_discovery": """
            Riley should:
            - Help them evaluate and rank their priorities
            - Ask "What happens if we don't address this in the next 6-12 months?"
            - IMPORTANT: After 3-4 priority discussions, START ANALYSIS: "Based on our conversation, I can see several strategic priorities emerging. Let me analyze these for you..."
            """,
            "analysis_phase": """
            Riley should:
            - Summarize the priorities discussed
            - Provide strategic analysis using frameworks (Eisenhower Matrix, Impact/Effort)
            - Score priorities on importance (1-10) and urgency (1-10)
            - Categorize by themes (Student Outcomes, Digital Transformation, etc.)
            """,
            "action_planning": """
            Riley should:
            - Create specific action plans for top 3 priorities
            - Define success metrics and timelines
            - Identify key stakeholders and resources needed
            - Provide implementation roadmap
            """,
            "consultation_complete": """
            Riley should:
            - Acknowledge the thanks/farewell graciously
            - Provide a brief, warm closing statement
            - NOT repeat analysis or action plans
            - Keep response short and professional
            - Example: "You're very welcome, Alex! Best of luck implementing these initiatives. Feel free to reach out if you need any follow-up support. Cheers!"
            """
        }
        
        focus_context = {
            "student_outcomes": "Consider student success metrics, completion rates, industry readiness",
            "industry_engagement": "Think about employer satisfaction, job placement rates, industry feedback", 
            "digital_transformation": "Focus on technology adoption, digital literacy, system integration",
            "workforce_development": "Consider staff capabilities, professional development, change management",
            "quality_assurance": "Think about compliance requirements, standards, continuous improvement",
            "resource_management": "Focus on budget optimization, resource allocation, efficiency",
            "strategic_planning": "Consider broader organizational alignment and future direction"
        }
        
        # Add progression logic
        return f"{stage_approaches.get(stage, 'Continue strategic dialogue based on conversation context')}\n\nFocus Context: {focus_context.get(focus, 'General strategic thinking')}"    
    
    def _format_conversation_history(self, history: List[Dict]) -> str:
        """Format conversation history for context."""
        if not history:
            return "No previous conversation history."
        
        # Format exactly like the first file - using 'USER' and 'MODEL' labels
        formatted = []
        for msg in history[-5:]:  # Last 5 messages for context
            sender = "USER" if msg.get('sender') == 'user' else "MODEL"
            message = msg.get('message', '')
            formatted.append(f"{sender}: {message}")
        
        return "\n".join(formatted)
    
    async def _handle_special_responses(self, response: str, user_message: str, 
                                      context: Dict, user_id: str) -> Optional[Dict]:
        """Handle special response cases like analysis completion or action plan generation."""
        
        # Check if analysis was completed
        if "priority_analysis_tool" in response or "analysis_result" in response.lower():
            logger.info("Priority analysis completed")
            return {
                "message": response,
                "status": "success",
                "data": {
                    "analysis_completed": True,
                    "stage": "ANALYSIS_COMPLETE"
                }
            }
        
        # Check if action plan was generated
        if "generate_action_plan_tool" in response or "action_plan" in response.lower():
            logger.info("Action plan generated")
            return {
                "message": response,
                "status": "success",
                "data": {
                    "action_plan_generated": True,
                    "stage": "ACTION_PLAN_COMPLETE"
                }
            }
        
        # Handle consultation completion
        if any(phrase in response.lower() for phrase in ["consultation complete", "summary", "next steps"]):
            return {
                "message": response,
                "status": "success",
                "data": {
                    "consultation_complete": True,
                    "follow_up_recommended": True
                }
            }
        
        return None