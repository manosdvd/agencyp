# validator.py
# This file contains the logic for validating a case file against a set of rules.

from dataclasses import dataclass, field
from typing import List, Literal
import schemas

# --- Type Definitions for Validator ---

RuleCategory = Literal["Ground Truth", "Referential Integrity", "Logical Consistency", "Playability"]
RuleSeverity = Literal["Error", "Warning"]

# --- Validator Schemas ---

@dataclass
class VerifierRule:
    ruleId: str
    category: RuleCategory
    severity: RuleSeverity
    description: str
    suggestion: str

@dataclass
class VerifierResult:
    rule: VerifierRule
    message: str
    offending_ids: List[str] = field(default_factory=list)

# --- Validator Class ---

class Validator:
    def __init__(self, rule_set: List[VerifierRule]):
        self.rules = {rule.ruleId: rule for rule in rule_set}
        self.validation_functions = {
            # Ground Truth
            "gt_victim_exists": self.validate_gt_victim_exists,
            "gt_perpetrator_exists": self.validate_gt_perpetrator_exists,
            "gt_motive_clue_exists": self.validate_gt_motive_clue_exists,
            "gt_means_clue_exists": self.validate_gt_means_clue_exists,
            "gt_opportunity_clue_exists": self.validate_gt_opportunity_clue_exists,
        }

    def validate(self, case_file: schemas.CaseFile) -> List[VerifierResult]:
        """Runs all validation rules against a case file."""
        results = []
        for rule_id, validation_func in self.validation_functions.items():
            if rule_id in self.rules:
                result = validation_func(case_file)
                if result:
                    results.append(result)
        return results

    # --- Ground Truth Validation Rules ---

    def validate_gt_victim_exists(self, case_file: schemas.CaseFile) -> VerifierResult | None:
        rule = self.rules["gt_victim_exists"]
        victim_id = case_file.groundTruth.victimId
        if not any(c.characterId == victim_id for c in case_file.characters):
            return VerifierResult(
                rule=rule,
                message=f"The victim ID '{victim_id}' defined in the Ground Truth does not correspond to any character in the case.",
                offending_ids=[victim_id]
            )
        return None

    def validate_gt_perpetrator_exists(self, case_file: schemas.CaseFile) -> VerifierResult | None:
        rule = self.rules["gt_perpetrator_exists"]
        perpetrator_id = case_file.groundTruth.perpetratorId
        if not any(c.characterId == perpetrator_id for c in case_file.characters):
            return VerifierResult(
                rule=rule,
                message=f"The perpetrator ID '{perpetrator_id}' defined in the Ground Truth does not correspond to any character in the case.",
                offending_ids=[perpetrator_id]
            )
        return None

    def validate_gt_motive_clue_exists(self, case_file: schemas.CaseFile) -> VerifierResult | None:
        rule = self.rules["gt_motive_clue_exists"]
        clue_id = case_file.groundTruth.motiveClueId
        if not any(c.clueId == clue_id for c in case_file.clues):
            return VerifierResult(
                rule=rule,
                message=f"The motive clue ID '{clue_id}' defined in the Ground Truth does not correspond to any clue in the case.",
                offending_ids=[clue_id]
            )
        return None
    
    def validate_gt_means_clue_exists(self, case_file: schemas.CaseFile) -> VerifierResult | None:
        rule = self.rules["gt_means_clue_exists"]
        clue_id = case_file.groundTruth.meansClueId
        if not any(c.clueId == clue_id for c in case_file.clues):
            return VerifierResult(
                rule=rule,
                message=f"The means clue ID '{clue_id}' defined in the Ground Truth does not correspond to any clue in the case.",
                offending_ids=[clue_id]
            )
        return None

    def validate_gt_opportunity_clue_exists(self, case_file: schemas.CaseFile) -> VerifierResult | None:
        rule = self.rules["gt_opportunity_clue_exists"]
        clue_id = case_file.groundTruth.opportunityClueId
        if not any(c.clueId == clue_id for c in case_file.clues):
            return VerifierResult(
                rule=rule,
                message=f"The opportunity clue ID '{clue_id}' defined in the Ground Truth does not correspond to any clue in the case.",
                offending_ids=[clue_id]
            )
        return None

# --- Rule Set Definition ---

def get_default_rule_set() -> List[VerifierRule]:
    """Returns the default set of validation rules."""
    return [
        # Ground Truth
        VerifierRule("gt_victim_exists", "Ground Truth", "Error", "Victim must be a valid character.", "Assign a valid character as the victim in the Ground Truth."),
        VerifierRule("gt_perpetrator_exists", "Ground Truth", "Error", "Perpetrator must be a valid character.", "Assign a valid character as the perpetrator in the Ground Truth."),
        VerifierRule("gt_motive_clue_exists", "Ground Truth", "Error", "Motive clue must be a valid clue.", "Assign a valid clue as the motive in the Ground Truth."),
        VerifierRule("gt_means_clue_exists", "Ground Truth", "Error", "Means clue must be a valid clue.", "Assign a valid clue as the means in the Ground Truth."),
        VerifierRule("gt_opportunity_clue_exists", "Ground Truth", "Error", "Opportunity clue must be a valid clue.", "Assign a valid clue as the opportunity in the Ground Truth."),
    ]
