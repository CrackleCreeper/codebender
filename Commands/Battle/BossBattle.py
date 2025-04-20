import random
import json

with open("./Structures/Skills.json", "r") as skill_data:
    skills = json.load(skill_data)
with open("./Structures/Bosses.json", "r") as boss_data:
    bosses = json.load(boss_data)

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

def BattleSequence(skills, bosses):
    # Get list of skill names from boss moves
    boss_move_names = [move["name"] for move in bosses["earth"]["moves"]]

    # Filter skills to only include those the boss knows
    skillList = [skill for skill in skills["earth"] if skill["name"] in boss_move_names]

    # Create battle sequence
    battle_sequence = makeBattleSequence(skillList)

    # Extract and print only the skill names from the battle sequence
    skill_names = [move["name"] for move in battle_sequence]
    return skill_names

print(json.dumps(BattleSequence(skills, bosses)))
