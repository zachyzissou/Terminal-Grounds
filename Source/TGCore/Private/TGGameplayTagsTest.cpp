#if WITH_AUTOMATION_TESTS

#include "Misc/AutomationTest.h"
#include "GameplayTagContainer.h"

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FTGGameplayTagsSanityTest, "TerminalGrounds.GameplayTags.Valid", EAutomationTestFlags::EditorContext | EAutomationTestFlags::SmokeFilter)

bool FTGGameplayTagsSanityTest::RunTest(const FString& Parameters)
{
    const FGameplayTag Tag = FGameplayTag::RequestGameplayTag(FName("TG.Faction.Corporate"), false);
    TestTrue(TEXT("TG.Faction.Corporate tag should be valid"), Tag.IsValid());
    return true;
}

#endif // WITH_AUTOMATION_TESTS
