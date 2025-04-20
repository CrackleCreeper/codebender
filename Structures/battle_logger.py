class BattleLogger:
    """
    A utility class to handle battle logging and status effect messages
    for the pet battle system.
    """
    
    def __init__(self):
        self.battle_log = []
        
    def clear_log(self):
        """Clear the battle log."""
        self.battle_log = []
        
    def add_entry(self, message):
        """Add an entry to the battle log."""
        self.battle_log.append(message)
        print(message)  # Print for immediate feedback
        
    def get_log(self, limit=None):
        """Get the battle log entries, optionally limited to the most recent ones."""
        if limit:
            return self.battle_log[-limit:]
        return self.battle_log
    
    # Status effect logging methods
    def log_stun(self, pet_name, duration):
        """Log when a pet is stunned."""
        self.add_entry(f"⚡ **{pet_name}** has been stunned for {duration} turn(s)!")
        
    def log_heal(self, pet_name, amount):
        """Log when a pet is healed."""
        self.add_entry(f"💚 **{pet_name}** healed for {amount} HP!")
        
    def log_dodge(self, pet_name):
        """Log when a pet dodges an attack."""
        self.add_entry(f"💨 **{pet_name}** dodged the attack!")
        
    def log_skipped_turn(self, pet_name, reason="stunned"):
        """Log when a pet's turn is skipped."""
        self.add_entry(f"⏭️ **{pet_name}** is {reason} and skips their turn!")
        
    def log_burst_used(self, pet_name, move_name, cooldown):
        """Log when a burst move is used."""
        self.add_entry(f"🔥 **{pet_name}** used burst move **{move_name}**! Cooldown: {cooldown} turns")
        
    def log_throttled_skill(self, pet_name, skill_type, cooldown):
        """Log cooldown information for throttled skills."""
        self.add_entry(f"⏱️ **{pet_name}**'s {skill_type} skills are on cooldown for {cooldown} more turn(s)")
        
    def log_attack(self, attacker_name, defender_name, move_name, damage, is_critical=False):
        """Log an attack with damage information."""
        critical_text = "💥 CRITICAL HIT! " if is_critical else ""
        self.add_entry(f"⚔️ **{attacker_name}** used **{move_name}** on **{defender_name}**! {critical_text}Dealt {damage:.1f} damage!")
        
    def log_buff(self, pet_name, buff_type, amount):
        """Log when a pet receives a buff."""
        emoji = "🔼" if amount > 0 else "🔽"
        buff_name = {"attack": "Attack", "defense": "Defense", "atkreduction": "Attack Reduction", "defreduction": "Defense Reduction"}
        self.add_entry(f"{emoji} **{pet_name}**'s {buff_name.get(buff_type, buff_type)} {'increased' if amount > 0 else 'decreased'} by {abs(amount)}!")
        
    def log_status_effect(self, pet_name, effect_name, duration=None):
        """Log when a status effect is applied."""
        duration_text = f" for {duration} turn(s)" if duration else ""
        self.add_entry(f"✨ **{pet_name}** is affected by **{effect_name}**{duration_text}!")

