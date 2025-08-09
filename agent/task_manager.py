"""
Task Manager for the Strategic Consultant Agent.
Handles consultation sessions and priority analysis.
"""

import os
import logging
import uuid
import json
from typing import Dict, Any, Optional, List # Import List

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
            conversation_history = context.get("conversationHistory", []) # Extract conversation history

            # Build comprehensive system instruction
            system_instruction = self._build_system_instruction(
                message, context, department, conversation_history # Pass conversation_history
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
            
            # Handle special cases like analysis completion
            response_result = await self._handle_special_responses(
                final_message, message, context, user_id # Use 'message' here
            )
            
            if response_result:
                return response_result
            
            return {
                "message": final_message,
                "status": "success",
                "session_id": session_id,
                "data": {
                    "conversation_stage": self._determine_conversation_stage(message), # Use 'message' here
                    "department": department
                }
            }
            
        except Exception as e:
            logger.error(f"Error processing task: {e}")
            return {
                "message": f"I apologize, but I encountered an error while processing your request: {str(e)}",
                "status": "error"
            }
    
    def _build_system_instruction(self, current_user_message: str, context: Dict, department: str, conversation_history: List[Dict]) -> str:
        """Build comprehensive system instruction for the agent."""
        
        # Determine conversation stage based on the current user message
        conversation_stage = self._determine_conversation_stage(current_user_message)
        
        # Get stage-specific instructions
        stage_instructions = self._get_stage_instructions(conversation_stage)
        
        # Format conversation history for the LLM
        # Ensure roles are 'user' or 'model' as expected by LLMs
        formatted_history = "\n".join([
            f"{'USER' if msg['sender'] == 'user' else 'MODEL'}: {msg['message']}" for msg in conversation_history
        ])
        
        return f"""
        You are Riley, a strategic consultant specializing in priority discovery and strategic planning.
        
        CURRENT CONSULTATION CONTEXT:
        - Department: {department}
        - Conversation Stage: {conversation_stage}
        - User ID: {context.get('user_id', 'unknown')}
        
        CONVERSATION HISTORY:
        {formatted_history}
        
        STAGE-SPECIFIC INSTRUCTIONS:
        {stage_instructions}
        
        CURRENT USER MESSAGE: "{current_user_message}"
        
        CONSULTATION GUIDELINES:
        1. Be professional yet approachable
        2. Ask strategic, insightful questions
        3. Listen actively and build on responses
        4. Provide clear summaries and recommendations
        5. Keep the consultation focused and time-efficient
        6. Always validate understanding before proceeding
        7. Use tools when appropriate for analysis
        
        ANALYSIS TOOLS AVAILABLE:
        - priority_analysis_tool: For scoring and analyzing strategic initiatives
        - generate_action_plan_tool: For creating actionable implementation plans
        
        Remember: Your goal is to help identify, analyze, and prioritize strategic initiatives effectively.
        """
    
    def _determine_conversation_stage(self, user_message: str) -> str:
        """Determine the current stage of the consultation based on the user message."""
        
        message_lower = user_message.lower()
        
        if any(keyword in message_lower for keyword in ["hello", "hi", "start", "begin", "consultation"]):
            return "INTRODUCTION"
        elif any(keyword in message_lower for keyword in ["department", "team", "organization", "challenges"]):
            return "DISCOVERY"
        elif any(keyword in message_lower for keyword in ["initiative", "project", "priority", "goal"]):
            return "EXPLORATION"
        elif any(keyword in message_lower for keyword in ["score", "rate", "important", "urgent", "rank"]):
            return "PRIORITIZATION"
        elif any(keyword in message_lower for keyword in ["analyze", "analysis", "summary", "results"]):
            return "ANALYSIS"
        elif any(keyword in message_lower for keyword in ["action", "plan", "next steps", "implementation"]):
            return "ACTION_PLANNING"
        else:
            return "GENERAL_INQUIRY"
    
    def _get_stage_instructions(self, stage: str) -> str:
        """Get dynamic instructions for the agent based on the current consultation stage."""
        
        instructions = {
            "INTRODUCTION": """
            - Introduce yourself warmly as Riley, strategic consultant
            - Explain the consultation process (15-20 minutes)
            - Ask about their department and what brings them to this consultation
            - Set expectations for the structured approach you'll take
            """,
            
            "DISCOVERY": """
            - Ask about the department, current challenges, and strategic goals
            - Identify key stakeholders and their perspectives
            - Gather information about existing initiatives and constraints
            - Listen for pain points and opportunities
            """,
            
            "EXPLORATION": """
            - Dive deeper into specific challenges and opportunities
            - Help articulate potential strategic initiatives
            - Ask probing questions about impact, urgency, and importance
            - Explore resource requirements and potential obstacles
            """,
            
            "PRIORITIZATION": """
            - Guide stakeholders to score initiatives on importance vs urgency (1-10 scale)
            - Clarify expected impact and effort required
            - Identify dependencies and interconnections
            - Prepare data for analysis tool
            """,
            
            "ANALYSIS": """
            - Use priority_analysis_tool to process gathered information
            - Present priority matrix and theme analysis
            - Highlight top 3 recommendations
            - Explain the scoring methodology
            """,
            
            "ACTION_PLANNING": """
            - Use generate_action_plan_tool to create downloadable summary
            - Provide next steps and implementation guidance
            - Discuss timeline and resource allocation
            - Offer follow-up consultation if needed
            """,
            
            "GENERAL_INQUIRY": """
            - Respond to general questions about strategic planning
            - Provide guidance based on best practices
            - Keep responses focused and actionable
            - Guide conversation toward structured consultation if appropriate
            """
        }
        
        return instructions.get(stage, instructions["GENERAL_INQUIRY"])
    
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


class SimpleCapacityTaskManager:
    """Simple Task Manager for the Capacity Assessment Agent."""
    
    def __init__(self, agent: Agent):
        """Initialize with an Agent instance and set up ADK Runner."""
        logger.info(f"Initializing SimpleCapacityTaskManager for agent: {agent.name}")
        self.agent = agent
        
        # Initialize ADK services
        self.session_service = InMemorySessionService()
        self.artifact_service = InMemoryArtifactService()
        
        # Create the runner with a different app name
        self.runner = Runner(
            agent=self.agent,
            app_name="capacity_assessment_app",
            session_service=self.session_service,
            artifact_service=self.artifact_service
        )
        logger.info(f"ADK Runner initialized for app '{self.runner.app_name}'")
    
    async def process_task(self, message: str, context: Dict[str, Any] = None, session_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Process a capacity assessment request.
        
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
            conversation_history = context.get("conversationHistory", [])

            # Build capacity assessment instruction
            system_instruction = self._build_capacity_instruction(message, conversation_history, department)
            
            # Create or generate session
            if not session_id:
                session_id = str(uuid.uuid4())
            
            # Create session
            try:
                await self.session_service.create_session(
                    app_name="capacity_assessment_app",
                    user_id=user_id,
                    session_id=session_id,
                    state={}
                )
            except Exception as e:
                logger.warning(f"Session creation issue: {e}")
            
            # Create user message
            request_content = adk_types.Content(
                role="user",
                parts=[adk_types.Part(text=system_instruction)]
            )
            
            # Run the agent
            events_async = self.runner.run_async(
                user_id=user_id,
                session_id=session_id,
                new_message=request_content
            )
            
            # Process response
            final_message = "Hello! I'm Morgan, your capacity analyst. Let's assess your department's current capacity and identify optimization opportunities. What department are we evaluating today?"
            
            async for event in events_async:
                if event.is_final_response() and event.content and event.content.role == "model":
                    if event.content.parts and event.content.parts[0].text:
                        final_message = event.content.parts[0].text
                        logger.info(f"Capacity agent response: {final_message}")
            
            return {
                "message": final_message,
                "status": "success",
                "session_id": session_id,
                "data": {
                    "agent_type": "capacity_assessment",
                    "conversation_stage": self._determine_assessment_stage(message),
                    "department": department
                }
            }
            
        except Exception as e:
            logger.error(f"Error processing capacity assessment task: {e}")
            return {
                "message": f"Hello! I'm Morgan, your capacity analyst. I encountered a technical issue, but let's proceed with your capacity assessment.",
                "status": "error"
            }
    
    def _build_capacity_instruction(self, current_user_message: str, conversation_history: List[Dict], department: str) -> str:
        """Build capacity assessment instruction for the agent."""
        
        # Format conversation history
        formatted_history = "\n".join([
            f"{'USER' if msg['sender'] == 'user' else 'MODEL'}: {msg['message']}" for msg in conversation_history
        ])
        
        # Determine assessment stage
        assessment_stage = self._determine_assessment_stage(current_user_message)
        
        return f"""
        You are Morgan, a capacity analyst specializing in departmental capacity assessment and optimization.
        
        CURRENT ASSESSMENT CONTEXT:
        - Department: {department}
        - Assessment Stage: {assessment_stage}
        
        CONVERSATION HISTORY:
        {formatted_history}
        
        CURRENT USER MESSAGE: "{current_user_message}"
        
        ASSESSMENT AREAS TO COVER:
        • Current staffing levels and workload distribution
        • Skills gaps and development opportunities
        • Process efficiency and workflow optimization
        • Resource allocation and utilization

        STAGE-SPECIFIC APPROACH:
        {self._get_assessment_stage_instructions(assessment_stage)}
        
        INSTRUCTIONS:
        - Ask focused, analytical questions (1-2 at a time)
        - Keep responses concise and data-focused (3-4 sentences maximum)
        - Focus on measurable outcomes and efficiency metrics
        - Guide toward concrete capacity improvement recommendations
        - Use specific terminology related to capacity management
        
        Remember: Your goal is to provide actionable capacity optimization recommendations.
        """
    
    def _determine_assessment_stage(self, user_message: str) -> str:
        """Determine the current stage of the capacity assessment."""
        
        message_lower = user_message.lower()
        
        if any(keyword in message_lower for keyword in ["hello", "hi", "start", "begin", "capacity"]):
            return "INTRODUCTION"
        elif any(keyword in message_lower for keyword in ["staff", "staffing", "team", "people", "headcount"]):
            return "STAFFING_ASSESSMENT"
        elif any(keyword in message_lower for keyword in ["skills", "training", "competency", "development", "gap"]):
            return "SKILLS_ANALYSIS"
        elif any(keyword in message_lower for keyword in ["process", "workflow", "efficiency", "bottleneck", "procedure"]):
            return "WORKFLOW_ANALYSIS"
        elif any(keyword in message_lower for keyword in ["resource", "allocation", "utilization", "optimization"]):
            return "RESOURCE_ANALYSIS"
        else:
            return "GENERAL_ASSESSMENT"
    
    def _get_assessment_stage_instructions(self, stage: str) -> str:
        """Get stage-specific instructions for capacity assessment."""
        
        instructions = {
            "INTRODUCTION": """
            - Introduce yourself as Morgan, capacity analyst
            - Explain the capacity assessment process and areas covered
            - Ask about the department and current capacity concerns
            """,
            
            "STAFFING_ASSESSMENT": """
            - Evaluate current staffing levels and workload distribution
            - Ask about team structure, roles, and responsibilities
            - Identify workload balance and staff utilization issues
            """,
            
            "SKILLS_ANALYSIS": """
            - Identify skills gaps and development opportunities
            - Assess current competencies vs. required capabilities
            - Explore training needs and knowledge transfer opportunities
            """,
            
            "WORKFLOW_ANALYSIS": """
            - Analyze current processes and workflow optimization opportunities
            - Identify bottlenecks and inefficient procedures
            - Focus on process improvement recommendations
            """,
            
            "RESOURCE_ANALYSIS": """
            - Evaluate resource allocation and utilization
            - Identify optimization opportunities and efficiency improvements
            - Provide actionable capacity enhancement recommendations
            """,
            
            "GENERAL_ASSESSMENT": """
            - Provide general capacity assessment guidance
            - Focus on comprehensive evaluation approach
            - Guide conversation toward specific assessment areas
            """
        }
        
        return instructions.get(stage, instructions["GENERAL_ASSESSMENT"])


class SimpleRiskTaskManager:
    """Simple Task Manager for the Risk Assessment Agent."""
    
    def __init__(self, agent: Agent):
        """Initialize with an Agent instance and set up ADK Runner."""
        logger.info(f"Initializing SimpleRiskTaskManager for agent: {agent.name}")
        self.agent = agent
        
        # Initialize ADK services
        self.session_service = InMemorySessionService()
        self.artifact_service = InMemoryArtifactService()
        
        # Create the runner with a different app name
        self.runner = Runner(
            agent=self.agent,
            app_name="risk_assessment_app",
            session_service=self.session_service,
            artifact_service=self.artifact_service
        )
        logger.info(f"ADK Runner initialized for app '{self.runner.app_name}'")
    
    async def process_task(self, message: str, context: Dict[str, Any] = None, session_id: Optional[str] = None) -> Dict[str, Any]:
        """Process a risk assessment request."""
        try:
            if not context:
                context = {}
            
            user_id = context.get("user_id", "default_user")
            department = context.get("department", "Unknown Department")
            conversation_history = context.get("conversationHistory", [])

            system_instruction = self._build_risk_instruction(message, conversation_history, department)
            
            if not session_id:
                session_id = str(uuid.uuid4())
            
            try:
                await self.session_service.create_session(
                    app_name="risk_assessment_app",
                    user_id=user_id,
                    session_id=session_id,
                    state={}
                )
            except Exception as e:
                logger.warning(f"Session creation issue: {e}")
            
            request_content = adk_types.Content(
                role="user",
                parts=[adk_types.Part(text=system_instruction)]
            )
            
            events_async = self.runner.run_async(
                user_id=user_id,
                session_id=session_id,
                new_message=request_content
            )
            
            final_message = "Hello! I'm Alex, your risk assessment specialist. Let's identify and assess potential risks in your department. What areas are you most concerned about?"
            
            async for event in events_async:
                if event.is_final_response() and event.content and event.content.role == "model":
                    if event.content.parts and event.content.parts[0].text:
                        final_message = event.content.parts[0].text
                        logger.info(f"Risk agent response: {final_message}")
            
            return {
                "message": final_message,
                "status": "success",
                "session_id": session_id,
                "data": {
                    "agent_type": "risk_assessment",
                    "conversation_stage": self._determine_risk_stage(message),
                    "department": department
                }
            }
            
        except Exception as e:
            logger.error(f"Error processing risk assessment task: {e}")
            return {
                "message": f"Hello! I'm Alex, your risk assessment specialist. I encountered a technical issue, but let's proceed with your risk assessment.",
                "status": "error"
            }
    
    def _build_risk_instruction(self, current_user_message: str, conversation_history: List[Dict], department: str) -> str:
        """Build risk assessment instruction for the agent."""
        
        formatted_history = "\n".join([
            f"{'USER' if msg['sender'] == 'user' else 'MODEL'}: {msg['message']}" for msg in conversation_history
        ])
        
        risk_stage = self._determine_risk_stage(current_user_message)
        
        return f"""
        You are Alex, a risk assessment specialist focusing on comprehensive risk management.
        
        CURRENT ASSESSMENT CONTEXT:
        - Department: {department}
        - Risk Assessment Stage: {risk_stage}
        
        CONVERSATION HISTORY:
        {formatted_history}
        
        CURRENT USER MESSAGE: "{current_user_message}"
        
        RISK ASSESSMENT AREAS:
        • Operational risks and potential failures
        • Compliance and regulatory risks
        • Strategic and financial risks
        • Mitigation strategies and contingency planning

        STAGE-SPECIFIC APPROACH:
        {self._get_risk_stage_instructions(risk_stage)}
        
        INSTRUCTIONS:
        - Ask systematic questions about potential vulnerabilities (1-2 at a time)
        - Keep responses structured and risk-focused (3-4 sentences maximum)
        - Focus on likelihood, impact, and risk controls
        - Guide toward comprehensive risk mitigation strategies
        - Use risk management terminology appropriately
        
        Remember: Your goal is to provide systematic risk management recommendations.
        """
    
    def _determine_risk_stage(self, user_message: str) -> str:
        """Determine the current stage of the risk assessment."""
        
        message_lower = user_message.lower()
        
        if any(keyword in message_lower for keyword in ["hello", "hi", "start", "begin", "risk"]):
            return "INTRODUCTION"
        elif any(keyword in message_lower for keyword in ["operational", "failure", "breakdown", "system"]):
            return "OPERATIONAL_RISKS"
        elif any(keyword in message_lower for keyword in ["compliance", "regulation", "legal", "audit"]):
            return "COMPLIANCE_RISKS"
        elif any(keyword in message_lower for keyword in ["strategic", "financial", "budget", "funding"]):
            return "STRATEGIC_RISKS"
        elif any(keyword in message_lower for keyword in ["mitigation", "control", "prevent", "manage"]):
            return "MITIGATION_PLANNING"
        else:
            return "GENERAL_RISK_ASSESSMENT"
    
    def _get_risk_stage_instructions(self, stage: str) -> str:
        """Get stage-specific instructions for risk assessment."""
        
        instructions = {
            "INTRODUCTION": """
            - Introduce yourself as Alex, risk assessment specialist
            - Explain the risk assessment process and areas covered
            - Ask about the department and immediate risk concerns
            """,
            
            "OPERATIONAL_RISKS": """
            - Identify operational risks and potential failures
            - Assess system vulnerabilities and process breakdowns
            - Explore service delivery risks and operational dependencies
            """,
            
            "COMPLIANCE_RISKS": """
            - Evaluate compliance and regulatory risks
            - Assess legal and audit-related exposures
            - Identify policy and procedural compliance gaps
            """,
            
            "STRATEGIC_RISKS": """
            - Analyze strategic and financial risks
            - Evaluate market, competitive, and reputational risks
            - Assess resource allocation and funding risks
            """,
            
            "MITIGATION_PLANNING": """
            - Develop mitigation strategies for identified risks
            - Plan contingency and recovery procedures
            - Establish risk monitoring and control measures
            """,
            
            "GENERAL_RISK_ASSESSMENT": """
            - Provide comprehensive risk assessment guidance
            - Focus on systematic risk identification and analysis
            - Guide conversation toward specific risk areas
            """
        }
        
        return instructions.get(stage, instructions["GENERAL_RISK_ASSESSMENT"])


class SimpleEngagementTaskManager:
    """Simple Task Manager for the Stakeholder Engagement Agent."""
    
    def __init__(self, agent: Agent):
        """Initialize with an Agent instance and set up ADK Runner."""
        logger.info(f"Initializing SimpleEngagementTaskManager for agent: {agent.name}")
        self.agent = agent
        
        # Initialize ADK services
        self.session_service = InMemorySessionService()
        self.artifact_service = InMemoryArtifactService()
        
        # Create the runner with a different app name
        self.runner = Runner(
            agent=self.agent,
            app_name="engagement_planning_app",
            session_service=self.session_service,
            artifact_service=self.artifact_service
        )
        logger.info(f"ADK Runner initialized for app '{self.runner.app_name}'")
    
    async def process_task(self, message: str, context: Dict[str, Any] = None, session_id: Optional[str] = None) -> Dict[str, Any]:
        """Process a stakeholder engagement planning request."""
        try:
            if not context:
                context = {}
            
            user_id = context.get("user_id", "default_user")
            department = context.get("department", "Unknown Department")
            conversation_history = context.get("conversationHistory", [])

            system_instruction = self._build_engagement_instruction(message, conversation_history, department)
            
            if not session_id:
                session_id = str(uuid.uuid4())
            
            try:
                await self.session_service.create_session(
                    app_name="engagement_planning_app",
                    user_id=user_id,
                    session_id=session_id,
                    state={}
                )
            except Exception as e:
                logger.warning(f"Session creation issue: {e}")
            
            request_content = adk_types.Content(
                role="user",
                parts=[adk_types.Part(text=system_instruction)]
            )
            
            events_async = self.runner.run_async(
                user_id=user_id,
                session_id=session_id,
                new_message=request_content
            )
            
            final_message = "G'day! I'm Jordan, your stakeholder engagement specialist. Let's develop a comprehensive engagement strategy. What project or initiative are you looking to engage stakeholders for?"
            
            async for event in events_async:
                if event.is_final_response() and event.content and event.content.role == "model":
                    if event.content.parts and event.content.parts[0].text:
                        final_message = event.content.parts[0].text
                        logger.info(f"Engagement agent response: {final_message}")
            
            return {
                "message": final_message,
                "status": "success",
                "session_id": session_id,
                "data": {
                    "agent_type": "engagement_planning",
                    "conversation_stage": self._determine_engagement_stage(message),
                    "department": department
                }
            }
            
        except Exception as e:
            logger.error(f"Error processing engagement planning task: {e}")
            return {
                "message": f"G'day! I'm Jordan, your engagement specialist. I encountered a technical issue, but let's proceed with your engagement planning.",
                "status": "error"
            }
    
    def _build_engagement_instruction(self, current_user_message: str, conversation_history: List[Dict], department: str) -> str:
        """Build engagement planning instruction for the agent."""
        
        formatted_history = "\n".join([
            f"{'USER' if msg['sender'] == 'user' else 'MODEL'}: {msg['message']}" for msg in conversation_history
        ])
        
        engagement_stage = self._determine_engagement_stage(current_user_message)
        
        return f"""
        You are Jordan, a stakeholder engagement expert specializing in comprehensive engagement planning.
        
        CURRENT PLANNING CONTEXT:
        - Department: {department}
        - Engagement Stage: {engagement_stage}
        
        CONVERSATION HISTORY:
        {formatted_history}
        
        CURRENT USER MESSAGE: "{current_user_message}"
        
        ENGAGEMENT PLANNING AREAS:
        • Stakeholder mapping and analysis
        • Engagement strategies and approaches
        • Communication channels and frequency
        • Timeline and resource requirements

        STAGE-SPECIFIC APPROACH:
        {self._get_engagement_stage_instructions(engagement_stage)}
        
        INSTRUCTIONS:
        - Ask strategic questions about stakeholder dynamics (1-2 at a time)
        - Keep responses practical and engagement-focused (3-4 sentences maximum)
        - Focus on building sustainable stakeholder relationships
        - Guide toward comprehensive engagement strategies
        - Use stakeholder engagement terminology appropriately
        
        Remember: Your goal is to create effective stakeholder engagement strategies.
        """
    
    def _determine_engagement_stage(self, user_message: str) -> str:
        """Determine the current stage of engagement planning."""
        
        message_lower = user_message.lower()
        
        if any(keyword in message_lower for keyword in ["hello", "hi", "start", "begin", "engagement"]):
            return "INTRODUCTION"
        elif any(keyword in message_lower for keyword in ["stakeholder", "group", "identify", "map"]):
            return "STAKEHOLDER_MAPPING"
        elif any(keyword in message_lower for keyword in ["strategy", "approach", "method", "engage"]):
            return "ENGAGEMENT_STRATEGY"
        elif any(keyword in message_lower for keyword in ["communication", "channel", "message", "frequency"]):
            return "COMMUNICATION_PLANNING"
        elif any(keyword in message_lower for keyword in ["timeline", "schedule", "implement", "resource"]):
            return "IMPLEMENTATION_PLANNING"
        else:
            return "GENERAL_ENGAGEMENT"
    
    def _get_engagement_stage_instructions(self, stage: str) -> str:
        """Get stage-specific instructions for engagement planning."""
        
        instructions = {
            "INTRODUCTION": """
            - Introduce yourself as Jordan, engagement planning expert
            - Explain the engagement planning process and areas covered
            - Ask about the project/initiative requiring stakeholder engagement
            """,
            
            "STAKEHOLDER_MAPPING": """
            - Identify key stakeholder groups and their influence levels
            - Assess stakeholder interests and engagement preferences
            - Map stakeholder relationships and interdependencies
            """,
            
            "ENGAGEMENT_STRATEGY": """
            - Design appropriate engagement approaches for different groups
            - Identify engagement methods and formats
            - Consider cultural and accessibility requirements
            """,
            
            "COMMUNICATION_PLANNING": """
            - Plan communication channels and frequency
            - Design messaging strategies for different audiences
            - Establish feedback collection mechanisms
            """,
            
            "IMPLEMENTATION_PLANNING": """
            - Create implementation timelines and milestones
            - Identify resource requirements and responsibilities
            - Establish success metrics and evaluation criteria
            """,
            
            "GENERAL_ENGAGEMENT": """
            - Provide comprehensive engagement planning guidance
            - Focus on sustainable stakeholder relationships
            - Guide conversation toward specific engagement areas
            """
        }
        
        return instructions.get(stage, instructions["GENERAL_ENGAGEMENT"])
