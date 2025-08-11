# DECISIONS

- Primary module: Using TGCore as the primary game module via IMPLEMENT_PRIMARY_GAME_MODULE for simplicity; can split a thin TerminalGrounds module later if desired.
- Engine: UE 5.4 baseline. GAS (GameplayAbilitySystem) planned; MassAI/EQS later.
- Data-driven: Tables and Primary Data Assets will drive balance/content; placeholder CSVs first.
- Server model: Server-authoritative with client prediction and rewind buffers (~200ms target).
