import random
import json

with open("./Structures/BossSkills.json", "r") as boss_skills_file:
    boss_skills = json.load(boss_skills_file)

def chooseBasicSkill(skillList):
    basicSkillList = [x for x in skillList if x["atktype"] == "Basic"]
    return random.choice(basicSkillList) if basicSkillList else None

def chooseBurstSkill(skillList):
    burstSkillList = [x for x in skillList if x["atktype"] == "Burst"]
    return random.choice(burstSkillList) if burstSkillList else None

def makeBattleSequence(skillList):
    basicCounter = 0
    moves = []
    for _ in range(50):
        if basicCounter < 3:
            skill = chooseBasicSkill(skillList)
            basicCounter += 1
        else:
            skill = chooseBurstSkill(skillList)
            basicCounter = 0
        if skill:
            moves.append(skill)
    return moves

def BattleSequence(boss_skills):
    # Get the first boss's skills
    boss_name = next(iter(boss_skills.keys()))
    skillList = boss_skills[boss_name]["skills"]
    
    # Create battle sequence
    battle_sequence = makeBattleSequence(skillList)
    
    # Extract and print only the skill names
    skill_names = [move["name"] for move in battle_sequence]
    return skill_names

print(json.dumps(BattleSequence(boss_skills)))