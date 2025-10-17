"""
Inclusive Gender and Orientation Support
Supports diverse identities and preferences
"""
from enum import Enum
from typing import List, Optional

class Gender(str, Enum):
    """Inclusive gender options"""
    MALE = "male"
    FEMALE = "female"
    NON_BINARY = "non_binary"
    GENDERQUEER = "genderqueer"
    GENDERFLUID = "genderfluid"
    AGENDER = "agender"
    PREFER_NOT_TO_SAY = "prefer_not_to_say"
    OTHER = "other"


class Orientation(str, Enum):
    """Sexual orientation options"""
    STRAIGHT = "straight"
    GAY = "gay"
    LESBIAN = "lesbian"
    BISEXUAL = "bisexual"
    PANSEXUAL = "pansexual"
    ASEXUAL = "asexual"
    QUESTIONING = "questioning"
    PREFER_NOT_TO_SAY = "prefer_not_to_say"
    OTHER = "other"


class MatchPreference(str, Enum):
    """Who user wants to match with"""
    MEN = "men"
    WOMEN = "women"
    NON_BINARY = "non_binary"
    EVERYONE = "everyone"


def get_compatible_genders(user_gender: str, user_orientation: str, match_preference: str) -> List[str]:
    """
    Determine compatible gender matches based on user's identity and preferences
    
    Args:
        user_gender: User's gender identity
        user_orientation: User's sexual orientation
        match_preference: Who user wants to match with
        
    Returns:
        List of compatible gender identities
    """
    # If user wants to match with everyone
    if match_preference == MatchPreference.EVERYONE:
        return list(Gender)
    
    # Specific preferences
    if match_preference == MatchPreference.MEN:
        return [Gender.MALE]
    
    if match_preference == MatchPreference.WOMEN:
        return [Gender.FEMALE]
    
    if match_preference == MatchPreference.NON_BINARY:
        return [
            Gender.NON_BINARY,
            Gender.GENDERQUEER,
            Gender.GENDERFLUID,
            Gender.AGENDER
        ]
    
    # Default: return all
    return list(Gender)


def calculate_compatibility_score(
    user1_gender: str,
    user1_orientation: str,
    user1_preferences: str,
    user1_age: int,
    user1_interests: List[str],
    user2_gender: str,
    user2_orientation: str,
    user2_preferences: str,
    user2_age: int,
    user2_interests: List[str]
) -> float:
    """
    Calculate compatibility score between two users
    
    Returns:
        Score between 0.0 and 1.0
    """
    score = 0.0
    
    # 1. Gender/orientation compatibility (40% weight)
    user1_compatible_genders = get_compatible_genders(user1_gender, user1_orientation, user1_preferences)
    user2_compatible_genders = get_compatible_genders(user2_gender, user2_orientation, user2_preferences)
    
    if user2_gender in user1_compatible_genders and user1_gender in user2_compatible_genders:
        score += 0.4
    
    # 2. Age compatibility (20% weight)
    age_diff = abs(user1_age - user2_age)
    if age_diff <= 3:
        score += 0.2
    elif age_diff <= 5:
        score += 0.15
    elif age_diff <= 10:
        score += 0.1
    
    # 3. Common interests (40% weight)
    if user1_interests and user2_interests:
        common_interests = set(user1_interests) & set(user2_interests)
        interest_ratio = len(common_interests) / max(len(user1_interests), len(user2_interests))
        score += 0.4 * interest_ratio
    
    return min(score, 1.0)


# UI labels for frontend
GENDER_LABELS = {
    Gender.MALE: "Male",
    Gender.FEMALE: "Female",
    Gender.NON_BINARY: "Non-Binary",
    Gender.GENDERQUEER: "Genderqueer",
    Gender.GENDERFLUID: "Genderfluid",
    Gender.AGENDER: "Agender",
    Gender.PREFER_NOT_TO_SAY: "Prefer not to say",
    Gender.OTHER: "Other"
}

ORIENTATION_LABELS = {
    Orientation.STRAIGHT: "Straight",
    Orientation.GAY: "Gay",
    Orientation.LESBIAN: "Lesbian",
    Orientation.BISEXUAL: "Bisexual",
    Orientation.PANSEXUAL: "Pansexual",
    Orientation.ASEXUAL: "Asexual",
    Orientation.QUESTIONING: "Questioning",
    Orientation.PREFER_NOT_TO_SAY: "Prefer not to say",
    Orientation.OTHER: "Other"
}
