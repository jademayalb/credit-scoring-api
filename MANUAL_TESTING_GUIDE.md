# Manual Testing Guide for POST Prediction Endpoints

This guide provides step-by-step instructions for manually testing the fixed POST prediction endpoints.

## Prerequisites
- Flask API is running on port 5800
- Access to the Streamlit dashboard (if testing integration)
- A REST client (curl, Postman, or browser developer tools)

## Test Case 1: POST /predict with client_id and feature modifications

### Expected Behavior
When modifying features for an existing client, the probability should reflect the changes made.

### Test Steps

1. **Get baseline prediction for client 100001**
   ```bash
   curl -X GET http://localhost:5800/predict/100001
   ```
   
   Expected response (example):
   ```json
   {
     "client_id": 100001,
     "probability": 0.322,
     "threshold": 0.5,
     "decision": "ACCEPTÉ",
     "model_name": "LightGBM",
     "status": "OK"
   }
   ```
   
   **Note the baseline probability (e.g., 32.2%)**

2. **Test modification with reduced AMT_CREDIT**
   ```bash
   curl -X POST http://localhost:5800/predict \
     -H "Content-Type: application/json" \
     -d '{
       "client_id": 100001,
       "features": {
         "AMT_CREDIT": 300000
       }
     }'
   ```
   
   Expected response:
   ```json
   {
     "client_id": 100001,
     "probability": <new_probability>,
     "threshold": 0.5,
     "decision": "ACCEPTÉ" or "REFUSÉ",
     "model_name": "LightGBM",
     "status": "OK",
     "input_features": {
       "AMT_CREDIT": 300000
     }
   }
   ```
   
   **Verify:** The probability may change based on the model's sensitivity to AMT_CREDIT.

3. **Check server logs**
   Look for log entries like:
   ```
   Modification appliquée: AMT_CREDIT = 300000
   POST /predict -> proba=0.XXXX client_id=100001 (features modifiées: ['AMT_CREDIT'])
   ```

## Test Case 2: POST /predict/<client_id> with feature modifications

### Expected Behavior
This endpoint should track modifications and return the changes in the response.

### Test Steps

1. **Get baseline for client 100001**
   ```bash
   curl -X GET http://localhost:5800/predict/100001
   ```

2. **Modify AMT_CREDIT via the client-specific endpoint**
   ```bash
   curl -X POST http://localhost:5800/predict/100001 \
     -H "Content-Type: application/json" \
     -d '{
       "features": {
         "AMT_CREDIT": 300000
       }
     }'
   ```
   
   Expected response:
   ```json
   {
     "client_id": 100001,
     "probability": <new_probability>,
     "threshold": 0.5,
     "decision": "ACCEPTÉ" or "REFUSÉ",
     "model_name": "LightGBM",
     "status": "OK",
     "input_features": {
       "AMT_CREDIT": 300000
     },
     "modifications_applied": {
       "AMT_CREDIT": {
         "old": 568800,
         "new": 300000
       }
     }
   }
   ```
   
   **Verify:**
   - `modifications_applied` field is present
   - Shows old and new values
   - Probability has changed (may be subtle depending on other features)

3. **Check server logs**
   Look for:
   ```
   Client 100001: AMT_CREDIT 568800 -> 300000
   POST /predict/100001 -> proba=0.XXXX (modif: ['AMT_CREDIT'])
   ```

## Test Case 3: Multiple feature modifications

### Test Steps

```bash
curl -X POST http://localhost:5800/predict/100001 \
  -H "Content-Type: application/json" \
  -d '{
    "features": {
      "AMT_CREDIT": 300000,
      "AMT_INCOME_TOTAL": 100000,
      "AMT_ANNUITY": 20000
    }
  }'
```

Expected response should include all three features in `modifications_applied`:
```json
{
  "modifications_applied": {
    "AMT_CREDIT": {"old": 568800, "new": 300000},
    "AMT_INCOME_TOTAL": {"old": 202500, "new": 100000},
    "AMT_ANNUITY": {"old": 24750, "new": 20000}
  }
}
```

## Test Case 4: Error handling - Non-existent client

```bash
curl -X POST http://localhost:5800/predict/999999999 \
  -H "Content-Type: application/json" \
  -d '{
    "features": {
      "AMT_CREDIT": 300000
    }
  }'
```

Expected response (404):
```json
{
  "erreur": "Client ID 999999999 introuvable",
  "status": "NOT_FOUND"
}
```

## Test Case 5: Error handling - Empty features

```bash
curl -X POST http://localhost:5800/predict \
  -H "Content-Type: application/json" \
  -d '{
    "client_id": 100001,
    "features": {}
  }'
```

Expected response (400):
```json
{
  "erreur": "Aucune feature fournie",
  "status": "INVALID_REQUEST"
}
```

## Test Case 6: New profile without client_id

```bash
curl -X POST http://localhost:5800/predict \
  -H "Content-Type: application/json" \
  -d '{
    "features": {
      "AMT_CREDIT": 500000,
      "AMT_INCOME_TOTAL": 150000,
      "AMT_ANNUITY": 25000
    }
  }'
```

Expected response:
```json
{
  "client_id": null,
  "probability": <probability>,
  "threshold": 0.5,
  "decision": "ACCEPTÉ" or "REFUSÉ",
  "status": "OK",
  "input_features": {
    "AMT_CREDIT": 500000,
    "AMT_INCOME_TOTAL": 150000,
    "AMT_ANNUITY": 25000
  }
}
```

## Integration Test with Streamlit Dashboard

If you have a Streamlit dashboard that uses these endpoints:

1. Navigate to the Simulation page
2. Select client 100001
3. Modify AMT_CREDIT from 568800 to 300000
4. Click the simulation button
5. **Verify:**
   - The probability updates (it should be different from the baseline)
   - The UI shows the new probability
   - Server logs show the modification

## Verification Checklist

- [ ] Baseline prediction works (GET /predict/<client_id>)
- [ ] POST /predict with client_id applies modifications correctly
- [ ] POST /predict/<client_id> applies modifications correctly
- [ ] modifications_applied field is present in response
- [ ] Server logs show detailed modification tracking
- [ ] Error handling works for non-existent clients
- [ ] Error handling works for empty features
- [ ] Multiple feature modifications are tracked correctly
- [ ] New profile prediction works (no client_id)
- [ ] Probability changes when significant features are modified

## Common Issues and Debugging

### Probability doesn't change
- Check if the feature you're modifying has significant importance in the model
- Try modifying multiple features at once (e.g., AMT_CREDIT + AMT_INCOME_TOTAL)
- Check server logs to confirm modifications are being applied

### Server errors
- Check if the model artifacts are loaded correctly
- Verify the GitHub CSV data is accessible
- Check server logs for detailed error messages

### Feature not being applied
- Verify the feature name matches exactly (case-sensitive)
- Check if the feature exists in the original client data
- Look for the "Modification appliquée" log message
