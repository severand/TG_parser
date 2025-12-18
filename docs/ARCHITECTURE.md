# TG Parser Architecture

## System Design

```
┌─────────────────────────────────────────────────────────────┐
│                        CLI Interface                        │
│                      (main.py - Click)                      │
└────────────┬────────────────────────────────────────┬────────┘
             │                                        │
      ┌──────▼──────┐                         ┌──────▼──────┐
      │   Search    │                         │    Parse    │
      │   Command   │                         │   Command   │
      └──────┬──────┘                         └──────┬──────┘
             │                                       │
      ┌──────▼──────────────────────────────────────▼──────┐
      │         Parser Orchestrator (Threading)           │
      │              core/parser.py                        │
      └──────┬─────────────────────────────────────────────┘
             │
      ┌──────▼──────────────────────────────────────────────┐
      │           Core Processing Layer                     │
      ├─────────────────────────────────────────────────────┤
      │  ┌─────────────────────────────────────────────┐    │
      │  │ Message Processor (HTML Parsing)           │    │
      │  │ - Text extraction                          │    │
      │  │ - Metadata parsing                         │    │
      │  │ - Context extraction                       │    │
      │  └─────────────────────────────────────────────┘    │
      │  ┌─────────────────────────────────────────────┐    │
      │  │ Search Engine (Relevance Scoring)          │    │
      │  │ - Keyword matching                         │    │
      │  │ - Filtering (date, views, hashtags)        │    │
      │  │ - Relevance calculation                    │    │
      │  └─────────────────────────────────────────────┘    │
      │  ┌─────────────────────────────────────────────┐    │
      │  │ Channel Handler                            │    │
      │  │ - Channel parsing                          │    │
      │  │ - Message extraction                       │    │
      │  └─────────────────────────────────────────────┘    │
      └──────┬────────────────────────────────────────────┬──┘
             │                                            │
      ┌──────▼────────────────────┐          ┌───────────▼──┐
      │  Network Layer            │          │ Data Layer   │
      ├──────────────────────────┤          ├──────────────┤
      │ - HTTP Client            │          │ - Models     │
      │ - Headers Rotator        │          │ - Storage    │
      │ - Session Handler        │          │ - Cache      │
      │ - Cookie Manager         │          │ - Deduplicate│
      │ - Delay Generator        │          └──────────────┘
      └──────┬────────────────────┘
             │
      ┌──────▼──────────────────────┐
      │  HTTP Requests (requests)   │
      │  Telegram Web              │
      └─────────────────────────────┘
```

---

## Module Organization

### Core (4 modules)
- **parser.py** - Main orchestrator, threading, statistics
- **message_processor.py** - HTML parsing, text/metadata extraction
- **search_engine.py** - Search logic, filtering, relevance scoring
- **channel_handler.py** - Channel-specific parsing

### Network (6 modules)
- **http_client.py** - HTTP requests with retry logic
- **headers_rotator.py** - User-Agent rotation
- **session_handler.py** - Session management
- **cookie_manager.py** - Cookie handling
- **delay_generator.py** - Random delays for anti-detection
- **user_agents.py** - User-Agent collection

### Data (4 modules)
- **models.py** - Dataclasses (Message, Channel, SearchResult)
- **storage.py** - Local file storage
- **cache.py** - In-memory caching
- **deduplicator.py** - Duplicate message removal

### Utils (3 modules)
- **logger.py** - Colored logging
- **validators.py** - Input validation
- **exceptions.py** - Custom exceptions

### Stats (2 modules)
- **collector.py** - Real-time statistics collection
- **reporter.py** - Report generation

### Output (4 modules)
- **console_output.py** - ANSI colored console output
- **table_formatter.py** - ASCII table formatting
- **json_exporter.py** - JSON export
- **csv_exporter.py** - CSV export

---

## Data Flow

```
Input: Channels + Keywords
   ↓
[Parser.parse_and_search]
   ├→ parse_channels() [Multi-threaded]
   │   ├→ Channel parsing
   │   └→ Message extraction
   ├→ search() 
   │   ├→ SearchEngine.search()
   │   ├→ Keyword matching
   │   ├→ Relevance scoring (0-100)
   │   └→ Filter application
   └→ Statistics collection
   ↓
Output: 
  - Search results (sorted by relevance)
  - Statistics (channels, messages, success rate)
  - Messages (raw data)
   ↓
[Export]
  ├→ JSON export
  ├→ CSV export
  └→ Console output
```

---

## Key Design Patterns

### 1. Multi-threading

```python
with ThreadPoolExecutor(max_workers=4) as executor:
    futures = [executor.submit(parse_channel, ch) for ch in channels]
    results = [f.result() for f in futures]
```

### 2. Relevance Scoring

```
Score = 
  (keyword_frequency / total_words) * 50 +  # Frequency
  (views / max_views) * 30 +                # Popularity
  (reactions / max_reactions) * 20          # Engagement
```

### 3. Filtering Pipeline

```
Messages → Filter Date → Filter Views → Filter Hashtags → Results
```

### 4. Anti-Detection

```
- Rotate User-Agent on each request
- Random delays (0.5-3 seconds)
- Session persistence with cookies
- Header rotation
```

---

## Performance Characteristics

| Operation | Time | Memory |
|-----------|------|--------|
| Single channel parse | 5-10s | 10-20MB |
| Search 1000 messages | <1s | 5-10MB |
| Export results | <500ms | <1MB |
| Threading (4 channels) | 2-3x faster | +5MB per thread |

---

## Scalability Considerations

### Current Limits
- Max concurrent threads: 4 (configurable)
- Max message cache: 10,000 (configurable)
- Max cookie storage: 100 cookies

### Future Improvements
- Database backend (PostgreSQL)
- Async/await instead of threading
- Message queue (Redis)
- Distributed processing
- Web UI
- REST API

---

## Security Features

✅ Anti-detection mechanisms  
✅ Cookie handling  
✅ Session management  
✅ Input validation  
✅ Error handling with graceful degradation  
✅ No credentials stored locally  

---

## Testing Strategy

- **Unit Tests:** 150+ (isolated component testing)
- **Integration Tests:** 12+ (component interaction)
- **Performance Tests:** 9+ (benchmarking)
- **Coverage Target:** 80%+

---

**Last Updated:** 2025-12-18
