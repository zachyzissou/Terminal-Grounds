#pragma once

#include "CoreMinimal.h"
#include "Components/ActorComponent.h"
#include "Net/UnrealNetwork.h"
#include "TicketPoolComponent.generated.h"

USTRUCT(BlueprintType)
struct FTicketPool
{
    GENERATED_BODY()

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Tickets")
    int32 AttackerTickets = 100;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Tickets")
    int32 DefenderTickets = 100;

    FTicketPool()
    {
        AttackerTickets = 100;
        DefenderTickets = 100;
    }
};

DECLARE_DYNAMIC_MULTICAST_DELEGATE_ThreeParams(FOnTicketsConsumed, bool, bIsAttacker, int32, TicketsConsumed, int32, TicketsRemaining);
DECLARE_DYNAMIC_MULTICAST_DELEGATE_OneParam(FOnTicketsExhausted, bool, bIsAttacker);
DECLARE_DYNAMIC_MULTICAST_DELEGATE_TwoParams(FOnTicketsRefilled, bool, bIsAttacker, int32, NewAmount);

/**
 * Ticket Pool Component
 * Manages attacker and defender ticket pools for siege victory conditions
 * Tickets represent reinforcement capacity - when exhausted, that side loses
 */
UCLASS(ClassGroup=(TG), meta=(BlueprintSpawnableComponent))
class TGTERRITORIAL_API UTicketPoolComponent : public UActorComponent
{
    GENERATED_BODY()

public:
    UTicketPoolComponent();

    // Events
    UPROPERTY(BlueprintAssignable, Category = "Siege|Events")
    FOnTicketsConsumed OnTicketsConsumed;

    UPROPERTY(BlueprintAssignable, Category = "Siege|Events")
    FOnTicketsExhausted OnTicketsExhausted;

    UPROPERTY(BlueprintAssignable, Category = "Siege|Events")
    FOnTicketsRefilled OnTicketsRefilled;

    // Ticket Management
    UFUNCTION(BlueprintCallable, Category = "Siege|Tickets", BlueprintAuthorityOnly)
    void ConsumeAttackerTickets(int32 Amount);

    UFUNCTION(BlueprintCallable, Category = "Siege|Tickets", BlueprintAuthorityOnly)
    void ConsumeDefenderTickets(int32 Amount);

    UFUNCTION(BlueprintCallable, Category = "Siege|Tickets", BlueprintAuthorityOnly)
    void RefillAttackerTickets(int32 Amount);

    UFUNCTION(BlueprintCallable, Category = "Siege|Tickets", BlueprintAuthorityOnly)
    void RefillDefenderTickets(int32 Amount);

    UFUNCTION(BlueprintCallable, Category = "Siege|Tickets", BlueprintAuthorityOnly)
    void ResetTickets();

    // Queries
    UFUNCTION(BlueprintPure, Category = "Siege|Tickets")
    int32 GetAttackerTickets() const { return Tickets.AttackerTickets; }

    UFUNCTION(BlueprintPure, Category = "Siege|Tickets")
    int32 GetDefenderTickets() const { return Tickets.DefenderTickets; }

    UFUNCTION(BlueprintPure, Category = "Siege|Tickets")
    bool IsAttackerExhausted() const { return Tickets.AttackerTickets <= 0; }

    UFUNCTION(BlueprintPure, Category = "Siege|Tickets")
    bool IsDefenderExhausted() const { return Tickets.DefenderTickets <= 0; }

    UFUNCTION(BlueprintPure, Category = "Siege|Tickets")
    float GetAttackerTicketPercentage() const;

    UFUNCTION(BlueprintPure, Category = "Siege|Tickets")
    float GetDefenderTicketPercentage() const;

    // Configuration
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Siege|Config")
    int32 InitialAttackerTickets = 100;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Siege|Config")
    int32 InitialDefenderTickets = 100;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Siege|Config")
    bool bAllowNegativeTickets = false;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Siege|Config")
    int32 TicketsPerRespawn = 1;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Siege|Config")
    int32 TicketsPerObjectiveLoss = 5;

    // Ticket Modifiers
    UFUNCTION(BlueprintCallable, Category = "Siege|Modifiers", BlueprintAuthorityOnly)
    void SetTicketConsumptionRate(float AttackerRate, float DefenderRate);

    UFUNCTION(BlueprintPure, Category = "Siege|Modifiers")
    void GetTicketConsumptionRates(float& OutAttackerRate, float& OutDefenderRate) const;

protected:
    virtual void BeginPlay() override;
    virtual void GetLifetimeReplicatedProps(TArray<FLifetimeProperty>& OutLifetimeProps) const override;

    UPROPERTY(ReplicatedUsing = OnRep_Tickets, BlueprintReadOnly, Category = "Siege|State")
    FTicketPool Tickets;

    UPROPERTY(Replicated, BlueprintReadOnly, Category = "Siege|State")
    float AttackerConsumptionRate;

    UPROPERTY(Replicated, BlueprintReadOnly, Category = "Siege|State")
    float DefenderConsumptionRate;

    UFUNCTION()
    void OnRep_Tickets();

private:
    FTicketPool PreviousTickets;

    void ConsumeTicketsInternal(bool bIsAttacker, int32 Amount);
    void RefillTicketsInternal(bool bIsAttacker, int32 Amount);
    void CheckExhaustion(bool bIsAttacker, int32 OldValue, int32 NewValue);
};