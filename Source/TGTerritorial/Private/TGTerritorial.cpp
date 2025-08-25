// Copyright Terminal Grounds. All Rights Reserved.

#include "TGTerritorial.h"
#include "Modules/ModuleManager.h"

IMPLEMENT_MODULE(FTGTerritorialModule, TGTerritorial);

DEFINE_LOG_CATEGORY(LogTGTerritorial);

void FTGTerritorialModule::StartupModule()
{
    UE_LOG(LogTGTerritorial, Log, TEXT("TGTerritorial Module Starting Up"));
    
    // Module initialization code here
    // Register components, initialize systems, etc.
}

void FTGTerritorialModule::ShutdownModule()
{
    UE_LOG(LogTGTerritorial, Log, TEXT("TGTerritorial Module Shutting Down"));
    
    // Module cleanup code here
}