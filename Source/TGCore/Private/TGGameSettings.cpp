#include "TGGameSettings.h"

UTGGameSettings::UTGGameSettings()
{
	CategoryName = TEXT("Game");
	SectionName = TEXT("TerminalGrounds");
}

const UTGGameSettings* UTGGameSettings::Get()
{
	return GetDefault<UTGGameSettings>();
}
