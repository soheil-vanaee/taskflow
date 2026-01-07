from rest_framework import serializers
from .models import SubscriptionPlan, UserSubscription, BillingHistory


class SubscriptionPlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubscriptionPlan
        fields = [
            'id', 'name', 'description', 'price', 
            'projects_limit', 'team_members_limit', 'tasks_limit',
            'features', 'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ('created_at', 'updated_at')


class UserSubscriptionSerializer(serializers.ModelSerializer):
    plan = SubscriptionPlanSerializer(read_only=True)
    plan_id = serializers.PrimaryKeyRelatedField(
        queryset=SubscriptionPlan.objects.all(),
        write_only=True
    )
    is_active_subscription = serializers.ReadOnlyField()
    days_until_expiry = serializers.ReadOnlyField()
    is_trial_period = serializers.ReadOnlyField()

    class Meta:
        model = UserSubscription
        fields = [
            'id', 'user', 'plan', 'plan_id', 'status', 
            'start_date', 'end_date', 'trial_end_date',
            'auto_renew', 'stripe_subscription_id',
            'is_active_subscription', 'days_until_expiry', 'is_trial_period',
            'created_at', 'updated_at'
        ]
        read_only_fields = ('user', 'created_at', 'updated_at')

    def create(self, validated_data):
        """
        Create a user subscription
        """
        validated_data['user'] = self.context['request'].user
        plan = validated_data.pop('plan_id')
        validated_data['plan'] = plan
        return UserSubscription.objects.create(**validated_data)


class BillingHistorySerializer(serializers.ModelSerializer):
    plan = SubscriptionPlanSerializer(read_only=True)
    plan_id = serializers.PrimaryKeyRelatedField(
        queryset=SubscriptionPlan.objects.all(),
        write_only=True
    )

    class Meta:
        model = BillingHistory
        fields = [
            'id', 'user', 'plan', 'plan_id', 'amount',
            'transaction_id', 'payment_method', 'status',
            'invoice_url', 'created_at'
        ]
        read_only_fields = ('user', 'created_at')

    def create(self, validated_data):
        """
        Create a billing history record
        """
        validated_data['user'] = self.context['request'].user
        plan = validated_data.pop('plan_id')
        validated_data['plan'] = plan
        return BillingHistory.objects.create(**validated_data)