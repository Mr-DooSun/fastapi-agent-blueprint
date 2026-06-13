# Webhook Receiver Example

An example application showing how to receive webhooks and process their payloads asynchronously in a background Taskiq worker task, keeping the HTTP response time fast.

## Pattern Explained

1. **Fast API Response:** When an external system hits `POST /v1/webhook`, the router writes the event to the database with `status="pending"` and enqueues a Taskiq worker job. It immediately returns `200 OK` without waiting for the slow processing to finish.
2. **Background Processing:** The worker runs the task, updates the event status to `"processing"`, simulates work (sleeps for 0.2s), generates a processing summary, and finally sets the status to `"done"`.
3. **Polling/Status Checking:** The client can query `GET /v1/webhook/{id}` at any time to inspect the current state of the webhook event.

---

## How to Run This Example

Because the blueprint's auto-discovery only scans `src/`, you run this example by copying it into `src/`:

```bash
# Copy example files
cp -r examples/webhook_receiver src/webhook_receiver

# Clean existing SQLite quickstart database so tables recreate on startup
rm -f ./quickstart.db

# Run the API server in one terminal
make quickstart
```

Open a second terminal and run the background worker:
```bash
# Run the worker process
make worker
```

Now, exercise the endpoints using `curl` in a separate terminal:

### 1. Send a webhook event
```bash
curl -i -X POST http://127.0.0.1:8001/v1/webhook \
  -H "Content-Type: application/json" \
  -d '{"source": "stripe", "payload": {"charge_id": "ch_123", "amount": 2999}}'
```

Response:
```json
{
  "success": true,
  "message": "Request processed successfully",
  "data": {
    "id": 1,
    "source": "stripe",
    "payload": {
      "charge_id": "ch_123",
      "amount": 2999
    },
    "status": "pending",
    "receivedAt": "2026-06-13T22:11:00",
    "processedAt": null
  }
}
```

### 2. Poll the status of the event
```bash
curl -sS http://127.0.0.1:8001/v1/webhook/1
```

Response (once completed by the background worker):
```json
{
  "success": true,
  "message": "Request processed successfully",
  "data": {
    "id": 1,
    "source": "stripe",
    "payload": {
      "charge_id": "ch_123",
      "amount": 2999,
      "processed_summary": "Processed event 1 from source '\''stripe'\'' at 2026-06-13 22:11:00.200000+00:00"
    },
    "status": "done",
    "receivedAt": "2026-06-13T22:11:00",
    "processedAt": "2026-06-13T22:11:00.200000"
  }
}
```

### 3. Clean up
Remove the example when you are done:
```bash
rm -rf src/webhook_receiver
rm -f ./quickstart.db
```

---

## Production References

Compare this lightweight example with the production-ready code in:
*   [src/user/interface/worker/tasks/user_test_task.py](file:///Users/vraj21/Desktop/fastapi-open-source/src/user/interface/worker/tasks/user_test_task.py) for the standard worker task wrapper pattern.
*   [src/_core/infrastructure/taskiq/](file:///Users/vraj21/Desktop/fastapi-open-source/src/_core/infrastructure/taskiq/) for the generic broker abstraction and dependency injection selectors.
