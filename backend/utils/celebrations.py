"""
Celebrations and Achievements System for Surveillance Drone
Tracks milestones, achievements, and celebrates user/system accomplishments.
"""

import json
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Any, Optional
from enum import Enum
from dataclasses import dataclass, asdict
import uuid


class AchievementType(Enum):
    """Types of achievements available."""
    FLIGHT = "flight"
    MISSION = "mission"
    DETECTION = "detection"
    EXPLORATION = "exploration"
    SYSTEM = "system"
    SAFETY = "safety"
    PERFORMANCE = "performance"
    MILESTONE = "milestone"


class AchievementTier(Enum):
    """Achievement difficulty tiers."""
    BRONZE = "bronze"
    SILVER = "silver"
    GOLD = "gold"
    PLATINUM = "platinum"
    LEGENDARY = "legendary"


@dataclass
class Achievement:
    """Achievement definition."""
    id: str
    name: str
    description: str
    type: AchievementType
    tier: AchievementTier
    criteria: Dict[str, Any]
    reward_points: int
    icon: str
    hidden: bool = False
    prerequisites: List[str] = None
    
    def __post_init__(self):
        if self.prerequisites is None:
            self.prerequisites = []


@dataclass
class UserAchievement:
    """User's earned achievement."""
    achievement_id: str
    user_id: str
    earned_at: str
    progress_data: Dict[str, Any]
    celebration_shown: bool = False


@dataclass
class UserProgress:
    """User's progress towards achievements."""
    user_id: str
    total_points: int
    achievements_earned: List[str]
    current_progress: Dict[str, Dict[str, Any]]
    statistics: Dict[str, Any]
    level: int
    experience: int


class CelebrationSystem:
    """Manages celebrations and achievements for the drone system."""
    
    def __init__(self):
        self.data_dir = Path("logs/achievements")
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        self.achievements_file = self.data_dir / "achievements.json"
        self.user_progress_file = self.data_dir / "user_progress.json"
        self.celebrations_file = self.data_dir / "celebrations.json"
        
        self.achievements = self._load_achievements()
        self.user_progress = self._load_user_progress()
        self.pending_celebrations = []
        
        self._initialize_default_achievements()
    
    def _load_achievements(self) -> Dict[str, Achievement]:
        """Load achievement definitions."""
        if self.achievements_file.exists():
            try:
                with open(self.achievements_file, 'r') as f:
                    data = json.load(f)
                    return {
                        aid: Achievement(**ach_data) 
                        for aid, ach_data in data.items()
                    }
            except Exception:
                pass
        return {}
    
    def _load_user_progress(self) -> Dict[str, UserProgress]:
        """Load user progress data."""
        if self.user_progress_file.exists():
            try:
                with open(self.user_progress_file, 'r') as f:
                    data = json.load(f)
                    return {
                        uid: UserProgress(**progress_data)
                        for uid, progress_data in data.items()
                    }
            except Exception:
                pass
        return {}
    
    def _save_achievements(self):
        """Save achievement definitions."""
        data = {aid: asdict(achievement) for aid, achievement in self.achievements.items()}
        with open(self.achievements_file, 'w') as f:
            json.dump(data, f, indent=2, default=str)
    
    def _save_user_progress(self):
        """Save user progress data."""
        data = {uid: asdict(progress) for uid, progress in self.user_progress.items()}
        with open(self.user_progress_file, 'w') as f:
            json.dump(data, f, indent=2, default=str)
    
    def _initialize_default_achievements(self):
        """Initialize default achievements if not already present."""
        default_achievements = [
            # Flight Achievements
            Achievement(
                id="first_flight",
                name="First Flight",
                description="Complete your first successful drone flight",
                type=AchievementType.FLIGHT,
                tier=AchievementTier.BRONZE,
                criteria={"flights_completed": 1},
                reward_points=50,
                icon="🚁"
            ),
            Achievement(
                id="flight_veteran",
                name="Flight Veteran",
                description="Complete 50 successful flights",
                type=AchievementType.FLIGHT,
                tier=AchievementTier.SILVER,
                criteria={"flights_completed": 50},
                reward_points=200,
                icon="✈️"
            ),
            Achievement(
                id="sky_master",
                name="Sky Master",
                description="Complete 200 flights and accumulate 50+ hours of flight time",
                type=AchievementType.FLIGHT,
                tier=AchievementTier.GOLD,
                criteria={"flights_completed": 200, "total_flight_time": 180000},
                reward_points=500,
                icon="🏆"
            ),
            
            # Mission Achievements
            Achievement(
                id="mission_rookie",
                name="Mission Rookie",
                description="Successfully complete your first surveillance mission",
                type=AchievementType.MISSION,
                tier=AchievementTier.BRONZE,
                criteria={"missions_completed": 1},
                reward_points=75,
                icon="🎯"
            ),
            Achievement(
                id="mission_commander",
                name="Mission Commander",
                description="Complete 25 surveillance missions with 95%+ success rate",
                type=AchievementType.MISSION,
                tier=AchievementTier.GOLD,
                criteria={"missions_completed": 25, "mission_success_rate": 0.95},
                reward_points=400,
                icon="🎖️"
            ),
            
            # Detection Achievements
            Achievement(
                id="eagle_eye",
                name="Eagle Eye",
                description="Successfully detect 100 objects during flights",
                type=AchievementType.DETECTION,
                tier=AchievementTier.SILVER,
                criteria={"objects_detected": 100},
                reward_points=150,
                icon="👁️"
            ),
            Achievement(
                id="surveillance_expert",
                name="Surveillance Expert",
                description="Detect 1000 objects with 90%+ accuracy",
                type=AchievementType.DETECTION,
                tier=AchievementTier.PLATINUM,
                criteria={"objects_detected": 1000, "detection_accuracy": 0.90},
                reward_points=750,
                icon="🔍"
            ),
            
            # Safety Achievements
            Achievement(
                id="safety_first",
                name="Safety First",
                description="Complete 10 flights without any safety incidents",
                type=AchievementType.SAFETY,
                tier=AchievementTier.BRONZE,
                criteria={"safe_flights": 10},
                reward_points=100,
                icon="🛡️"
            ),
            Achievement(
                id="incident_free",
                name="Incident Free",
                description="Operate for 30 days without safety incidents",
                type=AchievementType.SAFETY,
                tier=AchievementTier.GOLD,
                criteria={"incident_free_days": 30},
                reward_points=300,
                icon="⚡"
            ),
            
            # System Achievements
            Achievement(
                id="system_optimizer",
                name="System Optimizer",
                description="Achieve average system performance above 95%",
                type=AchievementType.PERFORMANCE,
                tier=AchievementTier.SILVER,
                criteria={"avg_system_performance": 0.95},
                reward_points=200,
                icon="⚙️"
            ),
            Achievement(
                id="night_owl",
                name="Night Owl",
                description="Complete 10 successful night missions",
                type=AchievementType.MISSION,
                tier=AchievementTier.SILVER,
                criteria={"night_missions": 10},
                reward_points=250,
                icon="🌙"
            ),
            
            # Milestone Achievements
            Achievement(
                id="drone_operator",
                name="Certified Drone Operator",
                description="Reach level 10 and earn 1000 points",
                type=AchievementType.MILESTONE,
                tier=AchievementTier.GOLD,
                criteria={"level": 10, "total_points": 1000},
                reward_points=500,
                icon="🎓"
            ),
            Achievement(
                id="legendary_pilot",
                name="Legendary Pilot",
                description="The ultimate drone operator - master of all aspects",
                type=AchievementType.MILESTONE,
                tier=AchievementTier.LEGENDARY,
                criteria={
                    "level": 25,
                    "total_points": 5000,
                    "flights_completed": 500,
                    "missions_completed": 100,
                    "objects_detected": 5000
                },
                reward_points=2000,
                icon="👑",
                hidden=True
            )
        ]
        
        # Add new achievements
        for achievement in default_achievements:
            if achievement.id not in self.achievements:
                self.achievements[achievement.id] = achievement
        
        self._save_achievements()
    
    def get_user_progress(self, user_id: str) -> UserProgress:
        """Get or create user progress."""
        if user_id not in self.user_progress:
            self.user_progress[user_id] = UserProgress(
                user_id=user_id,
                total_points=0,
                achievements_earned=[],
                current_progress={},
                statistics={
                    "flights_completed": 0,
                    "missions_completed": 0,
                    "objects_detected": 0,
                    "total_flight_time": 0,
                    "safe_flights": 0,
                    "mission_success_rate": 1.0,
                    "detection_accuracy": 0.0,
                    "avg_system_performance": 0.0,
                    "night_missions": 0,
                    "incident_free_days": 0,
                    "last_activity": datetime.now(timezone.utc).isoformat()
                },
                level=1,
                experience=0
            )
            self._save_user_progress()
        
        return self.user_progress[user_id]
    
    def update_user_stats(self, user_id: str, stats_update: Dict[str, Any]):
        """Update user statistics and check for achievements."""
        progress = self.get_user_progress(user_id)
        
        # Update statistics
        for key, value in stats_update.items():
            if key in progress.statistics:
                if isinstance(value, (int, float)):
                    if key in ["mission_success_rate", "detection_accuracy", "avg_system_performance"]:
                        # Handle rate/percentage updates
                        progress.statistics[key] = value
                    else:
                        # Handle incremental updates
                        progress.statistics[key] += value
                else:
                    progress.statistics[key] = value
        
        progress.statistics["last_activity"] = datetime.now(timezone.utc).isoformat()
        
        # Check for new achievements
        new_achievements = self._check_achievements(user_id)
        
        # Update level and experience
        self._update_level_and_experience(user_id)
        
        self._save_user_progress()
        
        return new_achievements
    
    def _check_achievements(self, user_id: str) -> List[Achievement]:
        """Check if user has earned any new achievements."""
        progress = self.user_progress[user_id]
        new_achievements = []
        
        for achievement_id, achievement in self.achievements.items():
            # Skip if already earned
            if achievement_id in progress.achievements_earned:
                continue
            
            # Check prerequisites
            if achievement.prerequisites:
                if not all(prereq in progress.achievements_earned 
                          for prereq in achievement.prerequisites):
                    continue
            
            # Check criteria
            if self._meets_criteria(progress.statistics, achievement.criteria):
                # Award achievement
                progress.achievements_earned.append(achievement_id)
                progress.total_points += achievement.reward_points
                
                new_achievements.append(achievement)
                
                # Create celebration
                self._create_celebration(user_id, achievement)
        
        return new_achievements
    
    def _meets_criteria(self, stats: Dict[str, Any], criteria: Dict[str, Any]) -> bool:
        """Check if statistics meet achievement criteria."""
        for key, required_value in criteria.items():
            if key not in stats:
                return False
            
            current_value = stats[key]
            
            if isinstance(required_value, (int, float)):
                if current_value < required_value:
                    return False
            else:
                if current_value != required_value:
                    return False
        
        return True
    
    def _update_level_and_experience(self, user_id: str):
        """Update user level based on points and activities."""
        progress = self.user_progress[user_id]
        
        # Calculate experience from various activities
        experience = (
            progress.statistics.get("flights_completed", 0) * 10 +
            progress.statistics.get("missions_completed", 0) * 25 +
            progress.statistics.get("objects_detected", 0) * 2 +
            progress.total_points
        )
        
        progress.experience = experience
        
        # Calculate level (exponential growth)
        level = 1
        required_exp = 100
        total_required = 0
        
        while experience >= total_required + required_exp:
            total_required += required_exp
            level += 1
            required_exp = int(required_exp * 1.2)  # 20% increase each level
        
        progress.level = level
    
    def _create_celebration(self, user_id: str, achievement: Achievement):
        """Create a celebration for earned achievement."""
        celebration = {
            "id": str(uuid.uuid4()),
            "user_id": user_id,
            "type": "achievement",
            "achievement_id": achievement.id,
            "achievement_name": achievement.name,
            "achievement_tier": achievement.tier.value,
            "achievement_icon": achievement.icon,
            "points_earned": achievement.reward_points,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "shown": False
        }
        
        self.pending_celebrations.append(celebration)
        
        # Save celebration
        self._save_celebration(celebration)
    
    def _save_celebration(self, celebration: Dict[str, Any]):
        """Save celebration to file."""
        celebrations = []
        
        if self.celebrations_file.exists():
            try:
                with open(self.celebrations_file, 'r') as f:
                    celebrations = json.load(f)
            except Exception:
                celebrations = []
        
        celebrations.append(celebration)
        
        # Keep only last 100 celebrations
        celebrations = celebrations[-100:]
        
        with open(self.celebrations_file, 'w') as f:
            json.dump(celebrations, f, indent=2, default=str)
    
    def get_pending_celebrations(self, user_id: str) -> List[Dict[str, Any]]:
        """Get pending celebrations for user."""
        return [
            celebration for celebration in self.pending_celebrations
            if celebration["user_id"] == user_id and not celebration["shown"]
        ]
    
    def mark_celebration_shown(self, celebration_id: str):
        """Mark celebration as shown."""
        for celebration in self.pending_celebrations:
            if celebration["id"] == celebration_id:
                celebration["shown"] = True
                break
    
    def get_achievements_by_type(self, achievement_type: AchievementType = None,
                                earned_only: bool = False, user_id: str = None) -> List[Achievement]:
        """Get achievements filtered by type and earned status."""
        achievements = list(self.achievements.values())
        
        if achievement_type:
            achievements = [a for a in achievements if a.type == achievement_type]
        
        if earned_only and user_id:
            progress = self.get_user_progress(user_id)
            achievements = [
                a for a in achievements 
                if a.id in progress.achievements_earned
            ]
        
        # Filter out hidden achievements unless earned
        if not earned_only or not user_id:
            achievements = [a for a in achievements if not a.hidden]
        elif user_id:
            progress = self.get_user_progress(user_id)
            achievements = [
                a for a in achievements 
                if not a.hidden or a.id in progress.achievements_earned
            ]
        
        return achievements
    
    def get_leaderboard(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get top users by points and achievements."""
        users = []
        
        for user_id, progress in self.user_progress.items():
            users.append({
                "user_id": user_id,
                "total_points": progress.total_points,
                "level": progress.level,
                "achievements_count": len(progress.achievements_earned),
                "flights_completed": progress.statistics.get("flights_completed", 0),
                "missions_completed": progress.statistics.get("missions_completed", 0)
            })
        
        # Sort by total points, then by level
        users.sort(key=lambda x: (-x["total_points"], -x["level"]))
        
        return users[:limit]
    
    def get_user_dashboard(self, user_id: str) -> Dict[str, Any]:
        """Get comprehensive user dashboard data."""
        progress = self.get_user_progress(user_id)
        
        # Get recent achievements
        recent_achievements = []
        if self.celebrations_file.exists():
            try:
                with open(self.celebrations_file, 'r') as f:
                    celebrations = json.load(f)
                    user_celebrations = [
                        c for c in celebrations 
                        if c["user_id"] == user_id and c["type"] == "achievement"
                    ]
                    user_celebrations.sort(key=lambda x: x["timestamp"], reverse=True)
                    recent_achievements = user_celebrations[:5]
            except Exception:
                pass
        
        # Calculate progress towards next level
        next_level_exp = self._calculate_next_level_experience(progress.level)
        current_level_exp = self._calculate_level_experience(progress.level)
        level_progress = (progress.experience - current_level_exp) / (next_level_exp - current_level_exp)
        
        return {
            "user_id": user_id,
            "level": progress.level,
            "experience": progress.experience,
            "total_points": progress.total_points,
            "achievements_earned": len(progress.achievements_earned),
            "level_progress": min(1.0, max(0.0, level_progress)),
            "next_level_exp_required": max(0, next_level_exp - progress.experience),
            "statistics": progress.statistics,
            "recent_achievements": recent_achievements,
            "pending_celebrations": self.get_pending_celebrations(user_id)
        }
    
    def _calculate_level_experience(self, level: int) -> int:
        """Calculate total experience required for a given level."""
        total_exp = 0
        required_exp = 100
        
        for l in range(1, level):
            total_exp += required_exp
            required_exp = int(required_exp * 1.2)
        
        return total_exp
    
    def _calculate_next_level_experience(self, current_level: int) -> int:
        """Calculate experience required for next level."""
        return self._calculate_level_experience(current_level + 1)


# Global celebration system instance
celebration_system = None

def init_celebration_system():
    """Initialize the global celebration system."""
    global celebration_system
    celebration_system = CelebrationSystem()
    return celebration_system

def get_celebration_system():
    """Get the global celebration system instance."""
    return celebration_system
