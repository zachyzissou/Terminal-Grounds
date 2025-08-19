#include "TGInterfaces.h"

#define LOCTEXT_NAMESPACE "FTGInterfacesModule"

void FTGInterfacesModule::StartupModule()
{
    // This module provides interfaces only
}

void FTGInterfacesModule::ShutdownModule()
{
    // Clean shutdown
}

#undef LOCTEXT_NAMESPACE
    
IMPLEMENT_MODULE(FTGInterfacesModule, TGInterfaces)