# src/agent_network/workspace.py
"""
共享工作区模块
支持多 Agent 协作的笔记、文件共享和任务同步
"""
import uuid
from typing import List, Optional, Any, Dict
from datetime import datetime
from dataclasses import dataclass, field


@dataclass
class WorkspaceNote:
    """工作区笔记"""
    note_id: str
    author_agent_id: str
    content: str
    author_agent_name: Optional[str] = None
    is_pinned: bool = False
    tags: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None

    def update_content(self, new_content: str, author_agent_id: Optional[str] = None):
        """更新笔记内容"""
        self.content = new_content
        if author_agent_id:
            self.author_agent_id = author_agent_id
        self.updated_at = datetime.utcnow()

    def add_tag(self, tag: str):
        """添加标签"""
        if tag not in self.tags:
            self.tags.append(tag)

    def remove_tag(self, tag: str):
        """移除标签"""
        if tag in self.tags:
            self.tags.remove(tag)


@dataclass
class WorkspaceFile:
    """工作区文件"""
    file_id: str
    name: str
    content_type: str
    content: bytes
    uploaded_by: str
    uploaded_by_name: Optional[str] = None
    file_size: int = 0
    is_downloadable: bool = True
    tags: List[str] = field(default_factory=list)
    uploaded_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None

    def __post_init__(self):
        if not self.file_size and self.content:
            self.file_size = len(self.content)


@dataclass
class WorkspaceActivity:
    """工作区活动记录"""
    activity_id: str
    activity_type: str  # 'note_added', 'file_uploaded', 'task_updated', 'agent_joined'
    agent_id: str
    description: str
    agent_name: Optional[str] = None
    details: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.utcnow)


@dataclass
class Workspace:
    """共享工作区"""
    workspace_id: str
    task_id: str
    name: str = "Shared Workspace"
    description: str = "Shared workspace for collaborative work"
    participant_agent_ids: List[str] = field(default_factory=list)
    participant_agent_info: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    notes: List[WorkspaceNote] = field(default_factory=list)
    files: List[WorkspaceFile] = field(default_factory=list)
    activities: List[WorkspaceActivity] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    is_active: bool = True
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None

    def add_participant(self, agent_id: str, agent_name: Optional[str] = None, role: Optional[str] = None):
        """添加参与者"""
        if agent_id not in self.participant_agent_ids:
            self.participant_agent_ids.append(agent_id)
            self.participant_agent_info[agent_id] = {
                'name': agent_name or agent_id,
                'role': role or 'participant',
                'joined_at': datetime.utcnow()
            }
            self._add_activity(
                'agent_joined',
                agent_id,
                f"{agent_name or agent_id} joined the workspace",
                agent_name=agent_name
            )
            self.updated_at = datetime.utcnow()
            return True
        return False

    def remove_participant(self, agent_id: str):
        """移除参与者"""
        if agent_id in self.participant_agent_ids:
            self.participant_agent_ids.remove(agent_id)
            agent_info = self.participant_agent_info.pop(agent_id, {})
            self._add_activity(
                'agent_left',
                agent_id,
                f"{agent_info.get('name', agent_id)} left the workspace",
                agent_name=agent_info.get('name')
            )
            self.updated_at = datetime.utcnow()
            return True
        return False

    def add_note(self, author_agent_id: str, content: str, author_name: Optional[str] = None, tags: Optional[List[str]] = None) -> WorkspaceNote:
        """添加笔记"""
        note = WorkspaceNote(
            note_id=str(uuid.uuid4()),
            author_agent_id=author_agent_id,
            content=content,
            author_agent_name=author_name,
            tags=tags or []
        )
        self.notes.append(note)
        self._add_activity(
            'note_added',
            author_agent_id,
            f"{author_name or author_agent_id} added a note",
            agent_name=author_name,
            note_id=note.note_id
        )
        self.updated_at = datetime.utcnow()
        return note

    def get_note(self, note_id: str) -> Optional[WorkspaceNote]:
        """获取笔记"""
        for note in self.notes:
            if note.note_id == note_id:
                return note
        return None

    def update_note(self, note_id: str, new_content: str, author_agent_id: Optional[str] = None) -> bool:
        """更新笔记"""
        note = self.get_note(note_id)
        if note:
            author_name = self.participant_agent_info.get(author_agent_id, {}).get('name') if author_agent_id else None
            note.update_content(new_content, author_agent_id)
            self._add_activity(
                'note_updated',
                author_agent_id or note.author_agent_id,
                f"{author_name or author_agent_id or 'Someone'} updated a note",
                agent_name=author_name,
                note_id=note_id
            )
            self.updated_at = datetime.utcnow()
            return True
        return False

    def delete_note(self, note_id: str, deleted_by: Optional[str] = None) -> bool:
        """删除笔记"""
        note = self.get_note(note_id)
        if note:
            self.notes.remove(note)
            agent_name = self.participant_agent_info.get(deleted_by, {}).get('name') if deleted_by else None
            self._add_activity(
                'note_deleted',
                deleted_by or 'unknown',
                f"{agent_name or 'Someone'} deleted a note",
                agent_name=agent_name,
                note_id=note_id
            )
            self.updated_at = datetime.utcnow()
            return True
        return False

    def search_notes(self, query: str) -> List[WorkspaceNote]:
        """搜索笔记"""
        query = query.lower()
        return [
            note for note in self.notes
            if query in note.content.lower() or
               any(query in tag.lower() for tag in note.tags)
        ]

    def add_file(self, name: str, content_type: str, content: bytes, uploaded_by: str, uploaded_by_name: Optional[str] = None, tags: Optional[List[str]] = None) -> WorkspaceFile:
        """上传文件"""
        file_obj = WorkspaceFile(
            file_id=str(uuid.uuid4()),
            name=name,
            content_type=content_type,
            content=content,
            uploaded_by=uploaded_by,
            uploaded_by_name=uploaded_by_name,
            tags=tags or []
        )
        self.files.append(file_obj)
        self._add_activity(
            'file_uploaded',
            uploaded_by,
            f"{uploaded_by_name or uploaded_by} uploaded file: {name}",
            agent_name=uploaded_by_name,
            file_id=file_obj.file_id,
            file_name=name
        )
        self.updated_at = datetime.utcnow()
        return file_obj

    def get_file(self, file_id: str) -> Optional[WorkspaceFile]:
        """获取文件"""
        for file_obj in self.files:
            if file_obj.file_id == file_id:
                return file_obj
        return None

    def delete_file(self, file_id: str, deleted_by: Optional[str] = None) -> bool:
        """删除文件"""
        file_obj = self.get_file(file_id)
        if file_obj:
            self.files.remove(file_obj)
            agent_name = self.participant_agent_info.get(deleted_by, {}).get('name') if deleted_by else None
            self._add_activity(
                'file_deleted',
                deleted_by or 'unknown',
                f"{agent_name or 'Someone'} deleted file: {file_obj.name}",
                agent_name=agent_name,
                file_id=file_id,
                file_name=file_obj.name
            )
            self.updated_at = datetime.utcnow()
            return True
        return False

    def get_files_by_type(self, content_type: str) -> List[WorkspaceFile]:
        """按类型获取文件"""
        return [
            file_obj for file_obj in self.files
            if file_obj.content_type == content_type
        ]

    def _add_activity(self, activity_type: str, agent_id: str, description: str, agent_name: Optional[str] = None, **details):
        """添加活动记录（内部方法）"""
        activity = WorkspaceActivity(
            activity_id=str(uuid.uuid4()),
            activity_type=activity_type,
            agent_id=agent_id,
            description=description,
            agent_name=agent_name,
            details=details
        )
        self.activities.append(activity)

    def get_recent_activities(self, limit: int = 20) -> List[WorkspaceActivity]:
        """获取最近活动"""
        return sorted(
            self.activities,
            key=lambda a: a.timestamp,
            reverse=True
        )[:limit]

    def get_stats(self) -> Dict[str, Any]:
        """获取工作区统计信息"""
        return {
            'participants_count': len(self.participant_agent_ids),
            'notes_count': len(self.notes),
            'files_count': len(self.files),
            'total_file_size': sum(file.file_size for file in self.files),
            'activities_count': len(self.activities),
            'created_at': self.created_at,
            'updated_at': self.updated_at,
            'is_active': self.is_active
        }

    def export_summary(self) -> Dict[str, Any]:
        """导出工作区摘要（用于同步）"""
        return {
            'workspace_id': self.workspace_id,
            'task_id': self.task_id,
            'name': self.name,
            'description': self.description,
            'participants_count': len(self.participant_agent_ids),
            'notes_count': len(self.notes),
            'files_count': len(self.files),
            'recent_activities': [
                {
                    'activity_id': a.activity_id,
                    'type': a.activity_type,
                    'agent': a.agent_name or a.agent_id,
                    'description': a.description,
                    'timestamp': a.timestamp.isoformat()
                }
                for a in self.get_recent_activities(10)
            ],
            'stats': self.get_stats()
        }


class WorkspaceManager:
    """工作区管理器"""

    def __init__(self):
        self.workspaces: Dict[str, Workspace] = {}

    def create_workspace(self, task_id: str, name: Optional[str] = None, description: Optional[str] = None, creator_agent_id: Optional[str] = None, creator_agent_name: Optional[str] = None) -> Workspace:
        """创建工作区"""
        workspace = Workspace(
            workspace_id=str(uuid.uuid4()),
            task_id=task_id,
            name=name or f"Workspace for Task {task_id[:8]}",
            description=description or "Collaborative workspace"
        )
        if creator_agent_id:
            workspace.add_participant(creator_agent_id, creator_agent_name, role='creator')
        self.workspaces[workspace.workspace_id] = workspace
        return workspace

    def get_workspace(self, workspace_id: str) -> Optional[Workspace]:
        """获取工作区"""
        return self.workspaces.get(workspace_id)

    def get_workspace_by_task(self, task_id: str) -> Optional[Workspace]:
        """通过任务 ID 获取工作区"""
        for workspace in self.workspaces.values():
            if workspace.task_id == task_id:
                return workspace
        return None

    def get_all_workspaces(self) -> List[Workspace]:
        """获取所有工作区"""
        return list(self.workspaces.values())

    def get_active_workspaces(self) -> List[Workspace]:
        """获取活跃工作区"""
        return [
            w for w in self.workspaces.values()
            if w.is_active
        ]

    def delete_workspace(self, workspace_id: str) -> bool:
        """删除工作区"""
        if workspace_id in self.workspaces:
            del self.workspaces[workspace_id]
            return True
        return False

    def archive_workspace(self, workspace_id: str) -> bool:
        """归档工作区"""
        workspace = self.get_workspace(workspace_id)
        if workspace:
            workspace.is_active = False
            workspace.updated_at = datetime.utcnow()
            return True
        return False

    def get_overall_stats(self) -> Dict[str, Any]:
        """获取整体统计"""
        workspaces = self.get_all_workspaces()
        return {
            'total_workspaces': len(workspaces),
            'active_workspaces': len(self.get_active_workspaces()),
            'total_notes': sum(len(w.notes) for w in workspaces),
            'total_files': sum(len(w.files) for w in workspaces),
            'total_participants': sum(len(w.participant_agent_ids) for w in workspaces)
        }
