#pragma once

#include "CoreMinimal.h"
#include "UObject/NoExportTypes.h"
#include "Engine/EngineTypes.h"
#include "Dom/JsonObject.h"
#include "Serialization/JsonSerializer.h"
#include "Serialization/JsonWriter.h"
#include "TGTerritorialManager.h"
#include "TGTerritorialWebSocketClient.generated.h"

USTRUCT(BlueprintType)
struct TGWORLD_API FTGTerritorialUpdate
{
    GENERATED_BODY()

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Territory")
    int32 TerritoryId;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Territory")
    int32 FactionId;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Territory")
    int32 InfluenceChange;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Territory")
    int32 StrategicValue;

    FTGTerritorialUpdate()
    {
        TerritoryId = 0;
        FactionId = 0;
        InfluenceChange = 0;
        StrategicValue = 1;
    }
};

USTRUCT(BlueprintType)
struct TGWORLD_API FTGTerritoryControlChange
{
    GENERATED_BODY()

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Territory")
    int32 TerritoryId;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Territory")
    FString TerritoryName;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Territory")
    int32 NewControllerFactionId;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Territory")
    FString NewControllerName;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Territory")
    FDateTime Timestamp;

    FTGTerritoryControlChange()
    {
        TerritoryId = 0;
        NewControllerFactionId = 0;
        Timestamp = FDateTime::Now();
    }
};

USTRUCT(BlueprintType)
struct TGWORLD_API FTGTerritoryContest
{
    GENERATED_BODY()

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Territory")
    int32 TerritoryId;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Territory")
    FString TerritoryName;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Territory")
    bool bContested;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Territory")
    FDateTime Timestamp;

    FTGTerritoryContest()
    {
        TerritoryId = 0;
        bContested = false;
        Timestamp = FDateTime::Now();
    }
};

DECLARE_DYNAMIC_MULTICAST_DELEGATE(FOnWebSocketConnected);
DECLARE_DYNAMIC_MULTICAST_DELEGATE(FOnWebSocketDisconnected);
DECLARE_DYNAMIC_MULTICAST_DELEGATE(FOnInitialStateReceived);
DECLARE_DYNAMIC_MULTICAST_DELEGATE_OneParam(FOnTerritoryControlChangedWebSocket, const FTGTerritoryControlChange&, ControlChange);
DECLARE_DYNAMIC_MULTICAST_DELEGATE_OneParam(FOnTerritoryContestedWebSocket, const FTGTerritoryContest&, Contest);
DECLARE_DYNAMIC_MULTICAST_DELEGATE_OneParam(FOnTerritoryDataUpdated, const FTGTerritoryData&, TerritoryData);

/**
 * WebSocket client for real-time territorial updates
 * Connects to territorial WebSocket server for live territorial state synchronization
 * Handles 100+ concurrent player environments with efficient message processing
 */
UCLASS(BlueprintType, Blueprintable)
class TGWORLD_API UTGTerritorialWebSocketClient : public UObject, public FTickableGameObject
{
    GENERATED_BODY()

public:
    UTGTerritorialWebSocketClient();

    // Initialization and cleanup
    UFUNCTION(BlueprintCallable, Category = "Territorial WebSocket")
    void Initialize();

    UFUNCTION(BlueprintCallable, Category = "Territorial WebSocket")
    void Deinitialize();

    // FTickableGameObject interface
    virtual void Tick(float DeltaTime) override;
    virtual TStatId GetStatId() const override { RETURN_QUICK_DECLARE_CYCLE_STAT(UTGTerritorialWebSocketClient, STATGROUP_Tickables); }
    virtual bool IsTickable() const override { return !IsTemplate(); }

    // Connection management
    UFUNCTION(BlueprintCallable, Category = "Territorial WebSocket")
    void ConnectToTerritorialServer();

    UFUNCTION(BlueprintCallable, Category = "Territorial WebSocket")
    void DisconnectFromServer();

    UFUNCTION(BlueprintCallable, Category = "Territorial WebSocket")
    bool IsConnected() const { return bConnected; }

    // Territorial updates
    UFUNCTION(BlueprintCallable, Category = "Territorial WebSocket")
    void SendTerritorialUpdate(const FTGTerritorialUpdate& Update);

    UFUNCTION(BlueprintCallable, Category = "Territorial WebSocket")
    void RequestTerritoryUpdate(int32 TerritoryId);

    // Configuration
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Connection")
    FString ServerURL;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Connection")
    bool bAutoReconnect;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Connection")
    float ReconnectDelay;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Connection")
    float PingInterval;

    // Events
    UPROPERTY(BlueprintAssignable, Category = "Territorial WebSocket Events")
    FOnWebSocketConnected OnConnected;

    UPROPERTY(BlueprintAssignable, Category = "Territorial WebSocket Events")
    FOnWebSocketDisconnected OnDisconnected;

    UPROPERTY(BlueprintAssignable, Category = "Territorial WebSocket Events")
    FOnInitialStateReceived OnInitialStateReceived;

    UPROPERTY(BlueprintAssignable, Category = "Territorial WebSocket Events")
    FOnTerritoryControlChangedWebSocket OnTerritoryControlChanged;

    UPROPERTY(BlueprintAssignable, Category = "Territorial WebSocket Events")
    FOnTerritoryContestedWebSocket OnTerritoryContested;

    UPROPERTY(BlueprintAssignable, Category = "Territorial WebSocket Events")
    FOnTerritoryDataUpdated OnTerritoryDataUpdated;

    // Statistics and monitoring
    UFUNCTION(BlueprintCallable, Category = "Territorial WebSocket")
    FString GetConnectionStats() const;

protected:
    // WebSocket handling
    void SendMessage(const FString& Message);
    void SendPing();
    void OnMessageReceived(const FString& Message);

    // Message handlers
    void HandlePongMessage(TSharedPtr<FJsonObject> JsonObject);
    void HandleInitialStateMessage(TSharedPtr<FJsonObject> JsonObject);
    void HandleTerritoryControlChanged(TSharedPtr<FJsonObject> JsonObject);
    void HandleTerritoryUpdate(TSharedPtr<FJsonObject> JsonObject);
    void HandleTerritoryContest(TSharedPtr<FJsonObject> JsonObject);

    // Data processing
    void ProcessTerritoryData(TSharedPtr<FJsonObject> TerritoryObject);

    // Connection events
    void OnConnectionEstablished();
    void OnConnectionLost();

private:
    // WebSocket connection (forward declared - will be implemented when WebSocket module is integrated)
    TSharedPtr<class IWebSocket> WebSocket;
    bool bConnected;

    // Timing
    float LastPingTime;
    double ConnectionStartTime;

    // Statistics
    int32 MessagesSent;
    int32 MessagesReceived;
};