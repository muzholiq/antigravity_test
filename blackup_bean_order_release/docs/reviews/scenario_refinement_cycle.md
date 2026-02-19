# Scenario Refinement & Documentation Review Cycle

**Participants:**
1.  **Order Manager (OM)**: Focus on usability, manual clarity, and error messages.
2.  **Product Lead (PL)**: Focus on business logic, edge case coverage, and requirements.
3.  **Roaster Customer (RC)**: Focus on operational procedures and physical realities.

---

## Round 1: Floating Point Quantity (OM)
*   **Context**: The recent update allows `Float` (e.g., 0.5kg).
*   **Feedback**: "User Manual says 'Integer only'. If I enter 0.5, will I get scolded?"
*   **Action**: Update `user_manual.md` to explicitly allow decimal inputs (0.5kg units).
*   **Status**: Completed

## Round 2: Sunday Delivery Warning (OM)
*   **Context**: Validator blocks Sunday.
*   **Feedback**: "I often forget dates. The manual should explicitly list 'No Sunday Delivery' as a rule, not just an error."
*   **Action**: Add "Sunday Delivery" to 'Common Mistakes' in `user_manual.md`.
*   **Status**: Completed

## Round 3: Editing Process (OM)
*   **Context**: `Status` column added (New/Processed).
*   **Feedback**: "If I make a mistake, can I just edit the cell? Does the system re-read 'Processed' rows?"
*   **Action**: Clarify in manual that 'Processed' rows are ignored; manual intervention needed or status reset (if allowed).
*   **Status**: Completed

## Round 4: Precision Tests (PL)
*   **Context**: Python float percision.
*   **Feedback**: "Does 0.1 + 0.2 equals 0.3? We need to ensure no floating point weirdness in reports."
*   **Action**: Add specific test case for Float summation in `scripts/test_runner.py`.
*   **Status**: Completed

## Round 5: Product-Roasting Constraints (PL)
*   **Context**: `ETH-YRG` only allows Light/Medium.
*   **Feedback**: "What if a new bean comes in? Do we need code change?"
*   **Action**: Confirm `settings.yaml` controls this and verify the test runner uses `settings.yaml` dynamically.
*   **Status**: Verified (Config driven).

## Round 6: Duplicate Orders (PL)
*   **Context**: Accidental double entry.
*   **Feedback**: "If I copy-paste the row twice, do I get double order? System should warn."
*   **Action**: Add 'Duplicate Order' detection test case to `test_runner.py` (even if logic isn't fully implemented, the test should exist as a requirement).
*   **Status**: Completed

## Round 7: Urgency Flag (RC)
*   **Context**: 'Urgent' column.
*   **Feedback**: "What does 'Urgent' actually change? Does it guarantee next day?"
*   **Action**: Clearly state in manual: "Urgent = Best Effort, not guaranteed".
*   **Status**: Completed

## Round 8: Status Column Visibility (RC)
*   **Context**: The system adds `Status` column.
*   **Feedback**: "Should the barista type in the 'Status' column? Or is it system reserved?"
*   **Action**: Add note in manual: "Do NOT touch Status/Timestamp columns".
*   **Status**: Completed

## Round 9: Architecture Update (RC)
*   **Context**: README says "No Scripts".
*   **Feedback**: "But we now have `validator.py` and `generate_data.py`. The README is lying."
*   **Action**: Update `README.md` to reflect the new "Hybrid Architecture" (Agent + Core Logic Scripts).
*   **Status**: Completed

## Round 10: Final Sign-off (All)
*   **Context**: Ready for V1.
*   **Feedback**: "If all above are fixed, we are good."
*   **Action**: Finalize all documents.
*   **Status**: Completed (All docs updated)
