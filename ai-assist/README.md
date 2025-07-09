```
uvicorn main:app --reload --port 8000
```

```
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{
        "intentcode": "create_objection_parking_fine",
        "message": "Goedemorgen, ik wil bezwaar maken.",
        "session_id": null
      }'
```