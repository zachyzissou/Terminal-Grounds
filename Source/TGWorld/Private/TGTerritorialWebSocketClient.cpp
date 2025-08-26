#include "TGTerritorialWebSocketClient.h"
#include "TGWorld.h"
#include "Engine/World.h"
#include "Misc/DateTime.h"

UTGTerritorialWebSocketClient::UTGTerritorialWebSocketClient()
{
    ServerURL = TEXT("ws://127.0.0.1:8765");
    bAutoReconnect = true;
    ReconnectDelay = 5.0f;
    PingInterval = 30.0f;
    LastPingTime = 0.0f;
    bConnected = false;
    WebSocket = nullptr;
}

void UTGTerritorialWebSocketClient::Initialize()
{
    UE_LOG(LogTGWorld, Log, TEXT("Initializing Territorial WebSocket Client"));
    
    // Initialize WebSocket connection
    ConnectToTerritorialServer();
}

void UTGTerritorialWebSocketClient::Deinitialize()
{
    UE_LOG(LogTGWorld, Log, TEXT("Deinitializing Territorial WebSocket Client"));
    
    if (WebSocket.IsValid() && WebSocket->IsConnected())
    {
        WebSocket->Close();
    }
    
    WebSocket.Reset();
    bConnected = false;
}

void UTGTerritorialWebSocketClient::Tick(float DeltaTime)
{
    // Handle periodic ping
    LastPingTime += DeltaTime;
    if (LastPingTime >= PingInterval && bConnected)
    {
        SendPing();
        LastPingTime = 0.0f;
    }
    
    // Handle auto-reconnect
    if (!bConnected && bAutoReconnect)
    {
        static float ReconnectTimer = 0.0f;
        ReconnectTimer += DeltaTime;
        
        if (ReconnectTimer >= ReconnectDelay)
        {
            UE_LOG(LogTGWorld, Log, TEXT("Attempting auto-reconnect to territorial server"));
            ConnectToTerritorialServer();
            ReconnectTimer = 0.0f;
        }
    }
}

void UTGTerritorialWebSocketClient::ConnectToTerritorialServer()
{
    if (bConnected)
    {
        return;
    }
    
    UE_LOG(LogTGWorld, Log, TEXT("Connecting to territorial server: %s"), *ServerURL);
    
    // TODO: Create WebSocket connection
    // This would typically use a WebSocket library like libwebsockets
    // For now, we simulate the connection
    
    bConnected = true;
    OnConnectionEstablished();
    
    UE_LOG(LogTGWorld, Log, TEXT("Connected to territorial server successfully"));
}

void UTGTerritorialWebSocketClient::DisconnectFromServer()
{
    if (!bConnected)
    {
        return;
    }
    
    UE_LOG(LogTGWorld, Log, TEXT("Disconnecting from territorial server"));
    
    if (WebSocket.IsValid())
    {
        WebSocket->Close();
    }
    
    bConnected = false;
    OnConnectionLost();
}

void UTGTerritorialWebSocketClient::SendTerritorialUpdate(const FTGTerritorialUpdate& Update)
{
    if (!bConnected)
    {
        UE_LOG(LogTGWorld, Warning, TEXT("Cannot send territorial update - not connected to server"));
        return;
    }
    
    // Create JSON message
    FString Message = FString::Printf(TEXT("{"
        "\"type\":\"influence_action\","
        "\"territory_id\":%d,"
        "\"faction_id\":%d,"
        "\"influence_change\":%d,"
        "\"strategic_value\":%d,"
        "\"timestamp\":\"%s\""
        "}"),
        Update.TerritoryId,
        Update.FactionId,
        Update.InfluenceChange,
        Update.StrategicValue,
        *FDateTime::Now().ToIso8601()
    );
    
    SendMessage(Message);
    
    UE_LOG(LogTGWorld, Log, TEXT("Sent territorial update: Territory %d, Faction %d, Change %d"),
           Update.TerritoryId, Update.FactionId, Update.InfluenceChange);
}

void UTGTerritorialWebSocketClient::RequestTerritoryUpdate(int32 TerritoryId)
{
    if (!bConnected)
    {
        return;
    }
    
    FString Message = FString::Printf(TEXT("{"
        "\"type\":\"request_update\","
        "\"territory_id\":%d"
        "}"), TerritoryId);
    
    SendMessage(Message);
}

void UTGTerritorialWebSocketClient::SendMessage(const FString& Message)
{
    if (!bConnected)
    {
        return;
    }
    
    // TODO: Send actual WebSocket message
    // For now, log the message that would be sent
    UE_LOG(LogTGWorld, VeryVerbose, TEXT("WebSocket Send: %s"), *Message);
    
    // Simulate message sending
    MessagesSent++;
}

void UTGTerritorialWebSocketClient::SendPing()
{
    if (!bConnected)
    {
        return;
    }
    
    FString PingMessage = FString::Printf(TEXT("{"
        "\"type\":\"ping\","
        "\"timestamp\":\"%s\""
        "}"), *FDateTime::Now().ToIso8601());
    
    SendMessage(PingMessage);
}

void UTGTerritorialWebSocketClient::OnMessageReceived(const FString& Message)
{
    UE_LOG(LogTGWorld, VeryVerbose, TEXT("WebSocket Received: %s"), *Message);
    
    // Parse JSON message
    TSharedPtr<FJsonObject> JsonObject;
    TSharedRef<TJsonReader<>> Reader = TJsonReaderFactory<>::Create(Message);
    
    if (!FJsonSerializer::Deserialize(Reader, JsonObject) || !JsonObject.IsValid())
    {
        UE_LOG(LogTGWorld, Warning, TEXT("Failed to parse WebSocket message: %s"), *Message);
        return;
    }
    
    FString MessageType = JsonObject->GetStringField(TEXT("type"));
    
    if (MessageType == TEXT("pong"))
    {
        HandlePongMessage(JsonObject);
    }
    else if (MessageType == TEXT("initial_state"))
    {
        HandleInitialStateMessage(JsonObject);
    }
    else if (MessageType == TEXT("territory_control_changed"))
    {
        HandleTerritoryControlChanged(JsonObject);
    }
    else if (MessageType == TEXT("territory_update"))
    {
        HandleTerritoryUpdate(JsonObject);
    }
    else if (MessageType == TEXT("territorial_contest"))
    {
        HandleTerritoryContest(JsonObject);
    }
    else
    {
        UE_LOG(LogTGWorld, Log, TEXT("Unknown message type: %s"), *MessageType);
    }
    
    MessagesReceived++;
}

void UTGTerritorialWebSocketClient::HandlePongMessage(TSharedPtr<FJsonObject> JsonObject)
{
    // Handle pong response - connection is alive
    UE_LOG(LogTGWorld, VeryVerbose, TEXT("Received pong from territorial server"));
}

void UTGTerritorialWebSocketClient::HandleInitialStateMessage(TSharedPtr<FJsonObject> JsonObject)
{
    UE_LOG(LogTGWorld, Log, TEXT("Received initial territorial state from server"));
    
    const TArray<TSharedPtr<FJsonValue>>* TerritoriesArray;
    if (JsonObject->TryGetArrayField(TEXT("territories"), TerritoriesArray))
    {
        for (const auto& TerritoryValue : *TerritoriesArray)
        {
            TSharedPtr<FJsonObject> TerritoryObject = TerritoryValue->AsObject();
            if (TerritoryObject.IsValid())
            {
                ProcessTerritoryData(TerritoryObject);
            }
        }
    }
    
    OnInitialStateReceived.Broadcast();
}

void UTGTerritorialWebSocketClient::HandleTerritoryControlChanged(TSharedPtr<FJsonObject> JsonObject)
{
    int32 TerritoryId = JsonObject->GetIntegerField(TEXT("territory_id"));
    FString TerritoryName = JsonObject->GetStringField(TEXT("territory_name"));
    int32 NewControllerId = JsonObject->GetIntegerField(TEXT("controller_faction_id"));
    FString ControllerName = JsonObject->GetStringField(TEXT("controller_name"));
    
    UE_LOG(LogTGWorld, Log, TEXT("Territory control changed: %s (%d) now controlled by %s (%d)"),
           *TerritoryName, TerritoryId, *ControllerName, NewControllerId);
    
    FTGTerritoryControlChange ControlChange;
    ControlChange.TerritoryId = TerritoryId;
    ControlChange.TerritoryName = TerritoryName;
    ControlChange.NewControllerFactionId = NewControllerId;
    ControlChange.NewControllerName = ControllerName;
    ControlChange.Timestamp = FDateTime::Now();
    
    OnTerritoryControlChanged.Broadcast(ControlChange);
}

void UTGTerritorialWebSocketClient::HandleTerritoryUpdate(TSharedPtr<FJsonObject> JsonObject)
{
    const TSharedPtr<FJsonObject>* TerritoryObject;
    if (JsonObject->TryGetObjectField(TEXT("territory"), TerritoryObject))
    {
        ProcessTerritoryData(*TerritoryObject);
    }
}

void UTGTerritorialWebSocketClient::HandleTerritoryContest(TSharedPtr<FJsonObject> JsonObject)
{
    int32 TerritoryId = JsonObject->GetIntegerField(TEXT("territory_id"));
    FString TerritoryName = JsonObject->GetStringField(TEXT("territory_name"));
    bool bContested = JsonObject->GetBoolField(TEXT("contested"));
    
    UE_LOG(LogTGWorld, Log, TEXT("Territory contest status: %s (%d) contested: %s"),
           *TerritoryName, TerritoryId, bContested ? TEXT("true") : TEXT("false"));
    
    FTGTerritoryContest Contest;
    Contest.TerritoryId = TerritoryId;
    Contest.TerritoryName = TerritoryName;
    Contest.bContested = bContested;
    Contest.Timestamp = FDateTime::Now();
    
    OnTerritoryContested.Broadcast(Contest);
}

void UTGTerritorialWebSocketClient::ProcessTerritoryData(TSharedPtr<FJsonObject> TerritoryObject)
{
    // Extract territory data and update local cache
    int32 TerritoryId = TerritoryObject->GetIntegerField(TEXT("territory_id"));
    FString TerritoryName = TerritoryObject->GetStringField(TEXT("territory_name"));
    int32 ControllerFactionId = TerritoryObject->GetIntegerField(TEXT("current_controller_faction_id"));
    FString ControllerName = TerritoryObject->GetStringField(TEXT("controller_name"));
    bool bContested = TerritoryObject->GetBoolField(TEXT("contested"));
    int32 StrategicValue = TerritoryObject->GetIntegerField(TEXT("strategic_value"));
    
    UE_LOG(LogTGWorld, VeryVerbose, TEXT("Processing territory data: %s (%d)"), *TerritoryName, TerritoryId);
    
    FTGTerritoryData TerritoryData;
    TerritoryData.TerritoryId = TerritoryId;
    TerritoryData.TerritoryName = TerritoryName;
    TerritoryData.CurrentControllerFactionId = ControllerFactionId;
    TerritoryData.bContested = bContested;
    TerritoryData.StrategicValue = StrategicValue;
    
    OnTerritoryDataUpdated.Broadcast(TerritoryData);
}

void UTGTerritorialWebSocketClient::OnConnectionEstablished()
{
    UE_LOG(LogTGWorld, Log, TEXT("WebSocket connection established with territorial server"));
    OnConnected.Broadcast();
}

void UTGTerritorialWebSocketClient::OnConnectionLost()
{
    UE_LOG(LogTGWorld, Warning, TEXT("WebSocket connection lost with territorial server"));
    OnDisconnected.Broadcast();
}

FString UTGTerritorialWebSocketClient::GetConnectionStats() const
{
    float Uptime = FPlatformTime::Seconds() - ConnectionStartTime;
    
    return FString::Printf(TEXT("WebSocket Stats - Connected: %s, Uptime: %.1fs, Sent: %d, Received: %d"),
                          bConnected ? TEXT("Yes") : TEXT("No"),
                          Uptime,
                          MessagesSent,
                          MessagesReceived);
}