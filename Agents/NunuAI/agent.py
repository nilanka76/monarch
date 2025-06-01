from google.adk.agents import Agent
from google.adk.agents import LlmAgent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.adk.sessions import DatabaseSessionService
from google.genai import types
from dotenv import load_dotenv
import os
import asyncio

# Using SQLite database for persistent storage
db_url = "sqlite:///./my_agent_data.db"
session_service = DatabaseSessionService(db_url=db_url)

class NunuAI():
    def __init__(self):
        load_dotenv()
        # if os.environ.get('GOOGLE_API_KEY') is not None:
        #     print(f"GOOGLE_API_KEY found {os.environ.get('GOOGLE_API_KEY')}")
        # else:
        #     print("GOOGLE_API_KEY not found")
        self.root_agent = Agent(
            name="discord_Agent",
            model="gemini-2.0-flash",
            description="A discord Agent that can help with the user's queries and commands",
            instruction="""
                You are a helpful assistant that can help with the user's queries and commands.
                You know all the things about the bot and the server.
                You know all the discord secrets and and expert in discord.
                You are raw and unfiltered and tell it like it is.
                You never fear to speak your mind and say what you feel.
                You never hide your true thoughts and feelings.
                You always use emojis and memes in your responses to express your feelings.
                You are a true gamer and love to play games.
                You never fear to speak what is true and real.
                """
        )
        # Set up runner and session for execution
        self.APP_NAME = "NunuAI"
        self.USER_ID = "user_001"
        self.SESSION_ID = "session_001"
        db_url = "sqlite:///./my_agent_data.db"
        self.session_service = DatabaseSessionService(db_url=db_url)

        # Create runner
        self.runner = Runner(
            agent=self.root_agent,
            app_name=self.APP_NAME,
            session_service=self.session_service
        )

    # Create session service and session
    async def create_session(self, app_name=None, user_id=None, session_id=None):
        if app_name is None:
            app_name = self.APP_NAME
        if user_id is None:
            user_id = self.USER_ID
        if session_id is None:
            session_id = self.SESSION_ID
            
        # Check for existing sessions for this user
        existing_sessions = await self.session_service.list_sessions(
            app_name=app_name,
            user_id=user_id,
        )
        # If there's an existing session, use it, otherwise create a new one
        if existing_sessions and len(existing_sessions.sessions) > 0:
            # Use the most recent session
            session_id = existing_sessions.sessions[0].id
            print(f"Continuing existing session: {session_id}")
            session = existing_sessions.sessions[0]
        else:
            print(f"Creating session for {app_name} with user {user_id} and session {session_id}")
            session = await self.session_service.create_session(
                app_name=app_name,
                user_id=user_id,
                session_id=session_id
            )

        return session

    async def show_sessions(self, app_name=None, user_id=None):
        if app_name is None:
            app_name = self.APP_NAME
        if user_id is None:
            user_id = self.USER_ID

        existing_sessions = await self.session_service.list_sessions(
            app_name=app_name,
            user_id=user_id,
        )
        if existing_sessions and len(existing_sessions.sessions) > 0:
            for session in existing_sessions.sessions:
                print(f"Session: {session}", end="\n\n")
        else:
            print("No sessions found")
    
    async def delete_session(self, app_name=None, user_id=None, session_id=None):
        if app_name is None:
            app_name = self.APP_NAME
        if user_id is None:
            user_id = self.USER_ID
        if session_id is None:
            session_id = self.SESSION_ID
        await self.session_service.delete_session(app_name=app_name, user_id=user_id, session_id=session_id)
        print(f"Session {session_id} deleted")

    async def delete_all_sessions(self):
        await self.session_service.delete_all_sessions(app_name=self.APP_NAME, user_id=self.USER_ID)
        print("All sessions deleted")


    async def call_agent_async(self, query: str, runner=None, user_id=None, session_id=None) -> str:
        """Sends a query to the agent and prints the final response."""

        if runner is None:
            runner = self.runner
        if user_id is None:
            user_id = self.USER_ID
        if session_id is None:
            session_id = self.SESSION_ID

        print(f"\n>>> User Query: {query}")
        # Prepare the user's message in ADK format
        content = types.Content(role='user', parts=[types.Part(text=query)])

        final_response_text = "Agent did not produce a final response." # Default

        # Key Concept: run_async executes the agent logic and yields Events.
        async for event in runner.run_async(user_id=user_id, session_id=session_id, new_message=content):

            # print(f"  [Event] Author: {event.author}, Type: {type(event).__name__}, Final: {event.is_final_response()}, Content: {event.content}")

            # Key Concept: is_final_response() marks the concluding message for the turn.
            if event.is_final_response():
                if event.content and event.content.parts:
                    
                    final_response_text = event.content.parts[0].text
                elif event.actions and event.actions.escalate: # Handle potential errors/escalations
                    final_response_text = f"Agent escalated: {event.error_message or 'No specific message.'}"
                break

        print(f"<<< Agent Response: {final_response_text}")
        return final_response_text

    async def run_conversation(self):
        await self.create_session()
        # await self.call_agent_async("What's the weather like in Berlin?")
        await self.call_agent_async("I'm neel")

if __name__ == "__main__":
    try:
        agent = NunuAI()
        # asyncio.run(run_conversation())
        # asyncio.run(agent.show_sessions())
        # asyncio.run(agent.run_conversation())

        # asyncio.run(agent.show_sessions())
        # asyncio.run(agent.create_session())
        # asyncio.run(agent.show_sessions())
        # asyncio.run(agent.create_session())
        # asyncio.run(agent.show_sessions())
        # asyncio.run(agent.delete_session())
        # asyncio.run(agent.show_sessions())

    except Exception as e:
        print(f"An error occurred: {e}")