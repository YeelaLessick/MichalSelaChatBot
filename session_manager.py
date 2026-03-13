"""
Session management module for handling session cleanup and persistence.
This module provides functionality to track, clean up, and persist chat sessions.
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, Any
from langchain_core.chat_history import BaseChatMessageHistory

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def persist_session_data(session_id: str, history: BaseChatMessageHistory, metadata: Dict[str, Any]):
    """
    Placeholder function for persisting session data before deletion.
    TODO: Implement CosmosDB or other storage persistence.
    
    Args:
        session_id: The session identifier
        history: The chat history to persist
        metadata: Session metadata (created_at, last_modified)
    """
    logger.info(f"💾 [Placeholder] Persisting session data for: {session_id}")
    logger.debug(f"   - Created: {metadata.get('created_at')}")
    logger.debug(f"   - Last modified: {metadata.get('last_modified')}")
    logger.debug(f"   - Message count: {len(history.messages)}")
    # Future implementation will save to CosmosDB
    pass


def cleanup_expired_sessions(session_storage: Dict[str, Any], timeout_minutes: int) -> int:
    """
    Removes sessions that haven't been active for timeout_minutes.
    Calls persist_session_data before deletion.
    
    Args:
        session_storage: The dictionary containing all sessions
        timeout_minutes: Number of minutes of inactivity before a session is considered expired
        
    Returns:
        Number of sessions cleaned up
    """
    current_time = datetime.now()
    timeout_delta = timedelta(minutes=timeout_minutes)
    sessions_to_remove = []
    
    # Find expired sessions
    for session_id, session_data in session_storage.items():
        last_modified = session_data.get("last_modified")
        if last_modified and (current_time - last_modified) > timeout_delta:
            inactive_minutes = int((current_time - last_modified).total_seconds() / 60)
            sessions_to_remove.append((session_id, session_data, inactive_minutes))
    
    # Remove expired sessions
    for session_id, session_data, inactive_minutes in sessions_to_remove:
        try:
            # Persist data before deletion
            persist_session_data(
                session_id,
                session_data["history"],
                {
                    "created_at": session_data.get("created_at"),
                    "last_modified": session_data.get("last_modified")
                }
            )
            
            # Delete from memory
            del session_storage[session_id]
            logger.info(f"🗑️  Expired session removed: session_id={session_id}, inactive_for={inactive_minutes}min")
            
        except Exception as e:
            logger.error(f"❌ Error removing session {session_id}: {e}")
    
    return len(sessions_to_remove)


def get_active_session_count(session_storage: Dict[str, Any]) -> int:
    """
    Returns the number of currently active sessions.
    
    Args:
        session_storage: The dictionary containing all sessions
        
    Returns:
        Number of active sessions in memory
    """
    return len(session_storage)


def get_session_statistics(session_storage: Dict[str, Any]) -> Dict[str, Any]:
    """
    Returns statistics about current sessions.
    
    Args:
        session_storage: The dictionary containing all sessions
        
    Returns:
        Dictionary containing session statistics
    """
    if not session_storage:
        return {
            "total_sessions": 0,
            "oldest_session": None,
            "newest_session": None,
            "average_message_count": 0
        }
    
    current_time = datetime.now()
    total_messages = 0
    oldest_time = None
    newest_time = None
    
    for session_data in session_storage.values():
        created_at = session_data.get("created_at")
        if created_at:
            if oldest_time is None or created_at < oldest_time:
                oldest_time = created_at
            if newest_time is None or created_at > newest_time:
                newest_time = created_at
        
        history = session_data.get("history")
        if history:
            total_messages += len(history.messages)
    
    return {
        "total_sessions": len(session_storage),
        "oldest_session_age_minutes": int((current_time - oldest_time).total_seconds() / 60) if oldest_time else None,
        "newest_session_age_minutes": int((current_time - newest_time).total_seconds() / 60) if newest_time else None,
        "average_message_count": total_messages / len(session_storage) if session_storage else 0,
        "total_messages": total_messages
    }
