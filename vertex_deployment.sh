#!/bin/bash

# --- Configuration Variables ---
CONFIG_FILE="language_learning_news_summary_agent/.agent_engine_config.json"

# --- Function to check and set GOOGLE_CLOUD_PROJECT if not set ---
check_project_id() {
    # Check if the environment variable is already set and non-empty
    if [ -z "$GOOGLE_CLOUD_PROJECT" ]; then
        echo "⚠️  GOOGLE_CLOUD_PROJECT environment variable is not set."
        while true; do
            read -r -p "Please enter your GOOGLE_CLOUD_PROJECT ID: " PROJECT_ID_INPUT
            if [[ -n "$PROJECT_ID_INPUT" ]]; then
                # Export the variable so the subsequent deployment command can use it
                export GOOGLE_CLOUD_PROJECT="$PROJECT_ID_INPUT"
                echo "✅ GOOGLE_CLOUD_PROJECT has been set for this session."
                break
            else
                echo "❌ Project ID cannot be empty. Please try again."
            fi
        done
    else
        echo "✅ Using existing GOOGLE_CLOUD_PROJECT: **$GOOGLE_CLOUD_PROJECT**"
    fi
    
    # Use the exported variable for the command base
    PROJECT_ID="$GOOGLE_CLOUD_PROJECT"
}

# --- Region Options ---
# Using a portable way to define and count regions
declare -A REGIONS
REGIONS[1]="europe-west1"
REGIONS[2]="europe-west4"
REGIONS[3]="us-east4"
REGIONS[4]="us-west1"
REGION_COUNT=${#REGIONS[@]}

# --- Main Script Logic ---

# 1. Check/Set Project ID
check_project_id

echo ""
echo "--- Vertex AI Region Selector ---"

# 2. Display available regions
echo "Please choose a deployment region for the Vertex Agent Engine:"
for i in "${!REGIONS[@]}"; do
  echo "$i) ${REGIONS[$i]}"
done
echo "---------------------------------"

# 3. Prompt for user choice
while true; do
  read -r -p "Enter your choice (1-${REGION_COUNT}): " choice
  
  # Validate input using a portable check (checks if the value exists)
  if [[ -n "${REGIONS[$choice]}" ]]; then
    SELECTED_REGION=${REGIONS[$choice]}
    echo "You selected: **$SELECTED_REGION**"
    break
  else
    echo "❌ Invalid choice. Please enter a number between 1 and ${REGION_COUNT}."
  fi
done

echo ""
echo "--- Executing Deployment Command ---"

# 4. Construct the full command
# $PROJECT_ID is now guaranteed to be set, either from env or user input

DEPLOY_COMMAND="adk deploy agent_engine --project=$PROJECT_ID --region=$SELECTED_REGION vertex --agent_engine_config_file=$CONFIG_FILE"

# Display the command before execution
echo "Command to run:"
echo "$DEPLOY_COMMAND"
echo ""

# 5. Execute the command
# Using 'eval' is necessary if you need complex shell expansion, but we use a direct execution here.
$DEPLOY_COMMAND

# 6. Check the exit status
if [ $? -eq 0 ]; then
  echo "✅ Deployment command completed successfully."
else
  echo "❌ Deployment command failed. Please check the output above for errors."
fi
