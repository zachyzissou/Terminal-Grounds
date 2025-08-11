#include "TGGameMode.h"
#include "TGCharacter.h"

ATGGameMode::ATGGameMode()
{
	DefaultPawnClass = ATGCharacter::StaticClass();
}
