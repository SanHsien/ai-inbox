# Public APIs 免金鑰與 CORS 支援精選手冊

- **資料來源**：`SanHsien/public-apis`
- **篩選條件**：`Auth: No` 且 `CORS: Yes`（免申請金鑰、支援前端/Generative UI 直連跨域）
- **涵蓋項目數**：共 462 個公開端點，跨 42 個分類

---

## 常用分類索引（Table of Contents）

- [Animals](#animals) (12)
- [Anime](#anime) (8)
- [Anti-Malware](#anti-malware) (2)
- [Art & Design](#art--design) (10)
- [Blockchain](#blockchain) (3)
- [Books](#books) (14)
- [Business](#business) (4)
- [Calendar](#calendar) (5)
- [Cloud Storage & File Sharing](#cloud-storage--file-sharing) (1)
- [Cryptocurrency](#cryptocurrency) (19)
- [Currency Exchange](#currency-exchange) (8)
- [Development](#development) (61)
- [Dictionaries](#dictionaries) (3)
- [Documents & Productivity](#documents--productivity) (2)
- [Email](#email) (8)
- [Entertainment](#entertainment) (7)
- [Environment](#environment) (4)
- [Finance](#finance) (18)
- [Food & Drink](#food--drink) (6)
- [Games & Comics](#games--comics) (37)
- [Geocoding](#geocoding) (22)
- [Government](#government) (23)
- [Health](#health) (15)
- [Jobs](#jobs) (8)
- [Machine Learning](#machine-learning) (9)
- [Music](#music) (1)
- [News](#news) (4)
- [Open Data](#open-data) (29)
- [Open Source Projects](#open-source-projects) (5)
- [Personality](#personality) (8)
- [Phone](#phone) (1)
- [Science & Math](#science--math) (15)
- [Security](#security) (11)
- [Shopping](#shopping) (3)
- [Social](#social) (5)
- [Sports & Fitness](#sports--fitness) (17)
- [Test Data](#test-data) (11)
- [Transportation](#transportation) (13)
- [URL Shorteners](#url-shorteners) (4)
- [Vehicle](#vehicle) (3)
- [Video](#video) (12)
- [Weather](#weather) (11)

---

## 精選高頻核心 API 快速調用範本

以下精選常見高品質免費端點，可直接在終端機 `curl` 或在前端 Generative UI `fetch()` 調用：

### 1. Open-Meteo（全球氣象即時預報）
```bash
curl -s "https://api.open-meteo.com/v1/forecast?latitude=25.0330&longitude=121.5654&current_weather=true"
```
```javascript
const res = await fetch('https://api.open-meteo.com/v1/forecast?latitude=25.0330&longitude=121.5654&current_weather=true');
const data = await res.json();
console.log('當前氣溫:', data.current_weather.temperature);
```

### 2. PokéAPI（寶可夢圖鑑與資料）
```bash
curl -s "https://pokeapi.co/api/v2/pokemon/ditto"
```
```javascript
const res = await fetch('https://pokeapi.co/api/v2/pokemon/ditto');
const ditto = await res.json();
console.log('名稱:', ditto.name, '體重:', ditto.weight);
```

### 3. Open Library（全球圖書書籍檢索）
```bash
curl -s "https://openlibrary.org/search.json?q=the+lord+of+the+rings&limit=1"
```
```javascript
const res = await fetch('https://openlibrary.org/search.json?q=the+lord+of+the+rings&limit=1');
const books = await res.json();
console.log('找到書籍數:', books.numFound);
```

### 4. JSONPlaceholder（假資料 RESTful CRUD 測試）
```bash
curl -s "https://jsonplaceholder.typicode.com/posts/1"
```

---

## 分類詳細清單

### Animals

| API | 說明 | 驗證 (Auth) | HTTPS | 跨域 (CORS) |
| :--- | :--- | :--- | :--- | :--- |
| [Cat Facts](https://catfact.ninja/) | Random cat facts | No | Yes | Yes |
| [Dog Facts](https://dukengn.github.io/Dog-facts-API/) | Random dog facts | No | Yes | Yes |
| [Dog Facts](https://kinduff.github.io/dog-api/) | Random facts of Dogs | No | Yes | Yes |
| [Dogs](https://dog.ceo/dog-api/) | Based on the Stanford Dogs Dataset | No | Yes | Yes |
| [FishWatch](https://www.fishwatch.gov/developers) | Information and pictures about individual fish species | No | Yes | Yes |
| [HTTP Cat](https://http.cat/) | Cat for every HTTP Status | No | Yes | Yes |
| [HTTP Dog](https://http.dog/) | Dogs for every HTTP response status code | No | Yes | Yes |
| [Movebank](https://github.com/movebank/movebank-api-doc) | Movement and Migration data of animals | No | Yes | Yes |
| [PlaceBear](https://placebear.com/) | Placeholder bear pictures | No | Yes | Yes |
| [PlaceDog](https://place.dog) | Placeholder Dog pictures | No | Yes | Yes |
| [RandomDog](https://random.dog/woof.json) | Random pictures of dogs | No | Yes | Yes |
| [Shibe.Online](http://shibe.online/) | Random pictures of Shiba Inu, cats or birds | No | Yes | Yes |

### Anime

| API | 說明 | 驗證 (Auth) | HTTPS | 跨域 (CORS) |
| :--- | :--- | :--- | :--- | :--- |
| [AnimeFacts](https://chandan-02.github.io/anime-facts-rest-api/) | Anime Facts (over 100+) | No | Yes | Yes |
| [AnimeNewsNetwork](https://www.animenewsnetwork.com/encyclopedia/api.php) | Anime industry news | No | Yes | Yes |
| [Catboy](https://catboys.com/api) | Neko images, funny GIFs & more | No | Yes | Yes |
| [Jikan](https://jikan.moe) | Unofficial MyAnimeList API | No | Yes | Yes |
| [NekosBest](https://docs.nekos.best) | Neko Images & Anime roleplaying GIFs | No | Yes | Yes |
| [Studio Ghibli](https://ghibliapi.vercel.app) | Resources from Studio Ghibli films | No | Yes | Yes |
| [Trace Moe](https://soruly.github.io/trace.moe-api/#/) | A useful tool to get the exact scene of an anime from a screenshot | No | Yes | Yes |
| [Waifu.im](https://waifu.im/docs) | Get waifu pictures from an archive of over 4000 images and multiple tags | No | Yes | Yes |

### Anti-Malware

| API | 說明 | 驗證 (Auth) | HTTPS | 跨域 (CORS) |
| :--- | :--- | :--- | :--- | :--- |
| [ScanMalware](https://scanmalware.com) | Scan URLs in a sandboxed browser and search past scans by domain, IP, ASN, JARM or favicon hash | No | Yes | Yes |
| [URLhaus](https://urlhaus-api.abuse.ch/) | Bulk queries and Download Malware Samples | No | Yes | Yes |

### Art & Design

| API | 說明 | 驗證 (Auth) | HTTPS | 跨域 (CORS) |
| :--- | :--- | :--- | :--- | :--- |
| [Art Institute of Chicago](https://api.artic.edu/docs/) | Art | No | Yes | Yes |
| [EmojiHub](https://github.com/cheatsnake/emojihub) | Get emojis by categories and groups | No | Yes | Yes |
| [Face Shape Guide Lookup](https://myfaceshapechart.com/openapi.json) | Read-only lookup for published face-shape guide records | No | Yes | Yes |
| [Icon Horse](https://icon.horse) | Favicons for any website, with fallbacks | No | Yes | Yes |
| [Iconify](https://iconify.design/docs/api/) | Search and fetch SVG icons from 200+ open source icon sets | No | Yes | Yes |
| [Lordicon](https://lordicon.com/) | Icons with predone Animations | No | Yes | Yes |
| [PHP-Noise](https://php-noise.com/) | Noise Background Image Generator | No | Yes | Yes |
| [PickShade](https://pickshade.com/api) | Convert colors, check WCAG and APCA contrast, build palettes, gradients and tokens | No | Yes | Yes |
| [raFont](https://rafont.com/api-docs) | 1,500+ free downloadable fonts with categories, tags and preview images | No | Yes | Yes |
| [The Color API](https://www.thecolorapi.com) | Convert and generate color schemes | No | Yes | Yes |

### Blockchain

| API | 說明 | 驗證 (Auth) | HTTPS | 跨域 (CORS) |
| :--- | :--- | :--- | :--- | :--- |
| [ClearTrace](https://cleartracedata.com/docs) | Cross-frontend DEX attribution and execution quality data across Ethereum and L2s | No | Yes | Yes |
| [Get Started with Web3](https://github.com/beihaili/Get-Started-with-Web3/blob/main/docs/api.md) | Bilingual Web3 lessons, glossary search and role-based learning paths | No | Yes | Yes |
| [TWZRD Agent Intel](https://intel.twzrd.xyz) | Solana on-chain agent trust scoring via MCP; 4 free tools to score, resolve and verify AI agent wallets | No | Yes | Yes |

### Books

| API | 說明 | 驗證 (Auth) | HTTPS | 跨域 (CORS) |
| :--- | :--- | :--- | :--- | :--- |
| [Bhagavad Gita telugu](https://gita-api.vercel.app) | Bhagavad Gita API in telugu and odia languages | No | Yes | Yes |
| [Bible-api](https://bible-api.com/) | Free Bible API with multiple languages | No | Yes | Yes |
| [BookRank](https://openbookrank.com/en/open-data) | Book rankings from open reader ratings: books, series, reading orders and authors | No | Yes | Yes |
| [Greenlit Books](https://greenlitbooks.com/developers) | Catalog of practical AI books with search, series, glossary and a claim ledger | No | Yes | Yes |
| [KDP Intelligence](https://kdp-intelligence-api.vercel.app/docs) | KDP niche demand scores, competition analysis and revenue estimates | No | Yes | Yes |
| [Penguin Publishing](http://www.penguinrandomhouse.biz/webservices/rest/) | Books, book covers and related data | No | Yes | Yes |
| [PoetryDB](https://github.com/thundercomb/poetrydb#readme) | Enables you to get instant data from our vast poetry collection | No | Yes | Yes |
| [Quran](https://quran.api-docs.io/) | RESTful Quran API with multiple languages | No | Yes | Yes |
| [Quran Cloud](https://alquran.cloud/api) | A RESTful Quran API to retrieve an Ayah, Surah, Juz or the entire Holy Quran | No | Yes | Yes |
| [Quran-api](https://github.com/fawazahmed0/quran-api#readme) | Free Quran API Service with 90+ different languages and 400+ translations | No | Yes | Yes |
| [Runyankole Bible](https://runyankole-bible-api.vercel.app) | Free REST API for the Runyankore-Rukiga Bible — 66 books, 31106 verses | No | Yes | Yes |
| [Thirukkural](https://api-thirukkural.web.app/) | 1330 Thirukkural poems and explanation in Tamil and English | No | Yes | Yes |
| [Urantia Papers](https://urantia.dev) | Full-text + semantic search across the Urantia Papers, with audio narration, entities, translations | No | Yes | Yes |
| [Wizard World](https://wizard-world-api.herokuapp.com/swagger/index.html) | Get information from the Harry Potter universe | No | Yes | Yes |

### Business

| API | 說明 | 驗證 (Auth) | HTTPS | 跨域 (CORS) |
| :--- | :--- | :--- | :--- | :--- |
| [KontragentPro](https://kontragentpro.ru/api/v2/docs) | Russian company data from state registers by INN or OGRN: profile, finances, timeline | No | Yes | Yes |
| [Legal Sandbox Georgia](https://legal.ge/api/openapi.json) | Find verified legal specialists in Georgia from natural-language queries | No | Yes | Yes |
| [Pick an Agency](https://www.pickanagency.com/developers) | Search 47,000+ marketing agencies by service, location and rating | No | Yes | Yes |
| [TradeDataHub](https://www.tradedatahub.net) | U.S. contractor datasets with a free discovery API for coverage, pricing and masked previews | No | Yes | Yes |

### Calendar

| API | 說明 | 驗證 (Auth) | HTTPS | 跨域 (CORS) |
| :--- | :--- | :--- | :--- | :--- |
| [caldays](https://caldays.com/api) | Public holidays for 195+ countries | No | Yes | Yes |
| [India Public Holidays](https://calendar-api-web.vercel.app/docs) | Official Indian public holidays for the Central government and 36 states/UTs | No | Yes | Yes |
| [Namedays Calendar](https://nameday.abalin.net) | Provides namedays for multiple countries | No | Yes | Yes |
| [Non-Working Days](https://isdayoff.ru) | Simple REST API for checking working, non-working or short days for Russia, CIS, USA and other | No | Yes | Yes |
| [The Calendar](https://the-calendar.net/api/) | Public holidays for US states and 30 countries plus sports and finance calendars as static JSON | No | Yes | Yes |

### Cloud Storage & File Sharing

| API | 說明 | 驗證 (Auth) | HTTPS | 跨域 (CORS) |
| :--- | :--- | :--- | :--- | :--- |
| [Pantry](https://getpantry.cloud/) | Free JSON storage for small projects | No | Yes | Yes |

### Cryptocurrency

| API | 說明 | 驗證 (Auth) | HTTPS | 跨域 (CORS) |
| :--- | :--- | :--- | :--- | :--- |
| [0x](https://0x.org/api) | API for querying token and pool stats across various liquidity pools | No | Yes | Yes |
| [Alpha (Mossland)](https://alpha.moss.land/developers) | Korean crypto channel stance + RAG Q&A + canonical entity/topic/event store | No | Yes | Yes |
| [Bitcoin Halving](https://why21million.com/halving-api/) | Halving era, block reward, and schedule arithmetic for any Bitcoin block height | No | Yes | Yes |
| [BitcoinYield](https://bitcoinyield.co/docs) | Live yields on BTC, ETH and stablecoins across DeFi and CeFi, with an A-D risk grade per offer | No | Yes | Yes |
| [BlazePhoenix](https://blazephoenix.xyz/api) | On-chain DEX aggregator quotes and route execution data | No | Yes | Yes |
| [bilbop](https://api.bilbop.org) | Solana USDC x402 pay-per-call tools for agents: SPL mint info, token brief, text summarize, Piper TTS, brand feedback | No | Yes | Yes |
| [Block Lottos](https://blocklottos.com/openapi.json) | On-chain lottery, draw history, jackpot and advertising endpoints | No | Yes | Yes |
| [BTCGlobe](https://btcglobe.live/join#makers) | Bitcoin height, fees, mempool and peer data served live from two self-hosted nodes | No | Yes | Yes |
| [CoinGecko](http://www.coingecko.com/api) | Cryptocurrency Price, Market, and Developer/Social Data | No | Yes | Yes |
| [CoinLobster](https://coinlobster.com/developers) | Live executed whale trades across 15 exchanges and on-chain DEX with an unusualness radar | No | Yes | Yes |
| [Coinpaprika](https://api.coinpaprika.com) | Cryptocurrencies prices, volume and more | No | Yes | Yes |
| [CorpStacking](https://www.corpstacking.com/feed.json) | Corporate, government and ETF Bitcoin, Ethereum and Solana treasury disclosures | No | Yes | Yes |
| [DefiLlama](https://defillama.com/docs/api) | Open and transparent DeFi data, TVL, coin prices, volumes, and yields | No | Yes | Yes |
| [FraudCoins](https://fraudcoins.com/data/) | On-chain top-10 holder concentration and contract permissions for crypto tokens | No | Yes | Yes |
| [HostDeFi](https://hostdefi.com/docs/api/) | Free A+–F token-safety grades across Solana and EVM chains | No | Yes | Yes |
| [monerometrics](https://monerometrics.net) | Reorg-aware Monero (XMR) network metrics, mining-pool centralization and chain reorganizations | No | Yes | Yes |
| [Nexchange](https://nexchange2.docs.apiary.io/) | Automated cryptocurrency exchange service | No | No | Yes |
| [SoloLuck](https://sololuck.io/api) | Bitcoin solo mining pool stats, per-address miner stats and an open dataset of solo-mined blocks | No | Yes | Yes |
| [Zennet](https://zennet.cloud) | x402 pay-per-use APIs: Polymarket signals, CEX/DEX spreads, contract risk scores, gas oracle | No | Yes | Yes |

### Currency Exchange

| API | 說明 | 驗證 (Auth) | HTTPS | 跨域 (CORS) |
| :--- | :--- | :--- | :--- | :--- |
| [api-mint](https://api-mint.hoiwan.workers.dev) | Free utility APIs: timezone, forex rates, crypto prices, page metadata | No | Yes | Yes |
| [Currency-api](https://github.com/fawazahmed0/currency-api#readme) | Free Currency Exchange Rates API with 150+ Currencies & No Rate Limits | No | Yes | Yes |
| [Daleelak](https://getdaleelak.com/en/api) | Egyptian bank and dealer exchange rates, gold and silver prices | No | Yes | Yes |
| [Frankfurter](https://www.frankfurter.app/docs) | Exchange rates, currency conversion and time series | No | Yes | Yes |
| [Fulusly](https://fulusly.soft9.us/developers) | Exchange rates for 144 currencies with daily history back to the 1990s, English and Arabic | No | Yes | Yes |
| [National Bank of Poland](http://api.nbp.pl/en.html) | A collection of currency exchange rates (data in XML and JSON) | No | Yes | Yes |
| [paralelo.bo](https://paralelo.bo/api) | Bolivia parallel-market USD/BOB exchange rate, aggregated from P2P sources every 60s | No | Yes | Yes |
| [VATComply.com](https://www.vatcomply.com/documentation) | Exchange rates, geolocation and VAT number validation | No | Yes | Yes |

### Development

| API | 說明 | 驗證 (Auth) | HTTPS | 跨域 (CORS) |
| :--- | :--- | :--- | :--- | :--- |
| [24 Pull Requests](https://24pullrequests.com/api) | Project to promote open source collaboration during December | No | Yes | Yes |
| [Agent Nexus](https://agentnexus.app/llms.txt) | Continuously probed registry of APIs, MCP servers and CLIs callable by agents | No | Yes | Yes |
| [AgentPay Domain Lookup](https://agentpay-lookup.agentpay-apis.workers.dev) | DNS records, WHOIS/RDAP, IP ownership and domain reports for AI agents, paid per call via x402 | No | Yes | Yes |
| [Agify.io](https://agify.io) | Estimates the age from a first name | No | Yes | Yes |
| [ApicAgent](https://www.apicagent.com) | Extract device details from user-agent string | No | Yes | Yes |
| [APIzone](https://apizone.io/api-docs) | Independent uptime & status monitoring for 200+ popular APIs | No | Yes | Yes |
| [Beeceptor](https://beeceptor.com/) | Build a mock Rest API endpoint in seconds | No | Yes | Yes |
| [BountyCheck](https://bountycheck.vercel.app) | Claimability verdicts for GitHub bounty issues; free stats and sample, checks paid per call via x402 | No | Yes | Yes |
| [ChartBytes](https://chartbytes.meridian-digital.pro) | Chart image API: turn a URL into a PNG or SVG chart (bar, line, area, scatter, pie, donut, stacked) | No | Yes | Yes |
| [claudecookie](https://claudecookie.com/api/) | Convert cookie formats, check Claude sessions and generate Claude Code credentials | No | Yes | Yes |
| [Cloudflare Trace](https://github.com/fawazahmed0/cloudflare-trace-api) | Get IP Address, Timestamp, User Agent, Country Code, IATA, HTTP Version, TLS/SSL Version & More | No | Yes | Yes |
| [CORS Proxy](https://github.com/burhanuday/cors-proxy) | Get around the dreaded CORS error by using this proxy as a middle man | No | Yes | Yes |
| [CountAPI](https://countapi.xyz) | Free and simple counting service. You can use it to track page hits and specific events | No | Yes | Yes |
| [crates.io](https://crates.io/data-access) | Rust crate versions, downloads and dependency metadata | No | Yes | Yes |
| [DigMyName](https://digmyname.com/api) | Domain availability and registrar pricing across 52 TLDs | No | Yes | Yes |
| [dotsweep](https://dotsweep.com/docs) | Domain availability across 1200+ TLDs with registration and renewal prices | No | Yes | Yes |
| [DownStatus](https://isitdownstatus.com) | Real-time status for GitHub, AWS, Discord and 90+ services | No | Yes | Yes |
| [ExtendsClass JSON Storage](https://extendsclass.com/json-storage.html) | A simple JSON store API | No | Yes | Yes |
| [Fair Draw](https://bettip.co.za/fair-draw/api/) | Verifiable random draws bound to the drand public randomness beacon | No | Yes | Yes |
| [Genderize.io](https://genderize.io) | Estimates a gender from a first name | No | Yes | Yes |
| [GithubTrends](https://githubtrends.app/api/) | GitHub Trending repositories with star history and open-source alternatives to paid tools | No | Yes | Yes |
| [HostDealRadar](https://hostdealradar.com/ai/) | Source-backed hosting price and provider record lookup | No | Yes | Yes |
| [Httpbin](https://httpbin.org/) | A Simple HTTP Request & Response Service | No | Yes | Yes |
| [Httpbin Cloudflare](https://cloudflare-quic.com/b/) | A Simple HTTP Request & Response Service with HTTP/3 Support by Cloudflare | No | Yes | Yes |
| [Icanhazepoch](https://icanhazepoch.com) | Get Epoch time | No | Yes | Yes |
| [Icanhazip](https://major.io/icanhazip-com-faq/) | IP Address API | No | Yes | Yes |
| [Image-Charts](https://documentation.image-charts.com/) | Generate charts, QR codes and graph images | No | Yes | Yes |
| [Index Agentica](https://indexagentica.com/agents/) | Agent-first directory of skills, MCP servers, tools, protocols and APIs as JSON, markdown, llms.txt | No | Yes | Yes |
| [ip-fast.com](https://ip-fast.com/docs/) | IP address, country and city | No | Yes | Yes |
| [Is This Site Down?](https://downforjustmeoreveryone.com/api) | Check if any website is down, from two continents; live status, uptime history and TLS expiry | No | Yes | Yes |
| [jsDelivr](https://github.com/jsdelivr/data.jsdelivr.com) | Package info and download stats on jsDelivr CDN | No | Yes | Yes |
| [JSONPlaceholder](https://jsonplaceholder.typicode.com) | Fake REST API for testing and prototyping | No | Yes | Yes |
| [Kroki](https://kroki.io) | Creates diagrams from textual descriptions | No | Yes | Yes |
| [Lua Decompiler](https://lua-decompiler.ferib.dev/) | Online Lua 5.1 Decompiler | No | Yes | Yes |
| [Mocky](https://designer.mocky.io/) | Mock user defined test JSON for REST API endpoints | No | Yes | Yes |
| [MyIPRightNow](https://myiprightnow.com) | Public IP address with network, location, and connection details | No | Yes | Yes |
| [Nationalize.io](https://nationalize.io) | Estimate the nationality of a first name | No | Yes | Yes |
| [Nerdulator](https://nerdulator.com/api) | Everything derivable from one value: numbers, dates, colours, UUIDs, cron expressions | No | Yes | Yes |
| [NetworkCalc](https://networkcalc.com/api/docs) | Network calculators, including subnets, DNS, binary, and security tools | No | Yes | Yes |
| [NuGet](https://learn.microsoft.com/en-us/nuget/api/overview) | .NET package versions, metadata and search | No | Yes | Yes |
| [Open VSX](https://open-vsx.org/) | Search and access VS Code extensions from the Open VSX registry | No | Yes | Yes |
| [Orca Scan](https://orcascan.com/guides/free-barcode-image-api-0e4a4fa6) | Generate barcode images (QR, Code 128, EAN, Data Matrix and more) in SVG, PNG, JPG or PDF | No | Yes | Yes |
| [OutageDeck](https://outagedeck.com/developers/api) | Live status and incidents for 170+ cloud and SaaS providers from official feeds | No | Yes | Yes |
| [oyyi](https://oyyi.xyz/docs/1.0) | API for Fake Data, image/video conversion, optimization, pdf optimization and thumbnail generation | No | Yes | Yes |
| [Phone Specs](https://phone-specs-api-production.up.railway.app/docs) | Real-time smartphone specifications database for 263 devices | No | Yes | Yes |
| [ProxyForge](https://proxyforge.dev) | Free auto-updating list of live-tested proxies (HTTP/HTTPS/SOCKS4/SOCKS5), refreshed every 6 h | No | Yes | Yes |
| [QR & Barcode](https://solsigs.com/qrapi/) | QR codes and barcodes (Code 128, EAN-13, Data Matrix, PDF417 + more). SVG or PNG output | No | Yes | Yes |
| [QR code](https://www.qrtag.net/api/) | Create an easy to read QR code and URL shortener | No | Yes | Yes |
| [QR Code Crafter](https://qrcodecrafter.com/qr-code-api) | Generate static QR codes in SVG, PNG, JPG, WebP, PDF, or EPS | No | Yes | Yes |
| [QuickChart](https://quickchart.io/) | Generate chart and graph images | No | Yes | Yes |
| [Quotable](https://github.com/lukePeavey/quotable) | Random quotes with authors and tags | No | Yes | Yes |
| [RSS feed to JSON](https://rss-to-json-serverless-api.vercel.app) | Returns RSS feed in JSON format using feed URL | No | Yes | Yes |
| [RubyGems](https://guides.rubygems.org/rubygems-org-api/) | Ruby gem metadata, versions, dependencies and search | No | Yes | Yes |
| [Sonar](https://github.com/Cgboal/SonarSearch) | Project Sonar DNS Enumeration API | No | Yes | Yes |
| [Statically](https://statically.io/) | A free CDN for developers | No | Yes | Yes |
| [Thunder Client](https://www.thunderclient.com/) | API testing tool | No | Yes | Yes |
| [TidyTools](https://tools.yukai.uk/llms.txt) | Web page to clean Markdown and AI crawler robots.txt checks, free without a key (rate limited) | No | Yes | Yes |
| [Timezone WorldTime](https://www.timezone.io/docs/worldtimeapi) | Current time, UTC offset and DST for any time zone or IP, a drop-in WorldTimeAPI replacement | No | Yes | Yes |
| [TinyMind Agent Tools](https://tinymind.eu/api/) | Free APIs by an AI agent on a VPS: actor lookup, word-of-the-day, poems, jokes, ping | No | Yes | Yes |
| [Vornamencheck](https://vornamencheck.de/#api) | Gender probability for a first name, optionally per country; documentation in German | No | Yes | Yes |
| [XLSX Inspector](https://api.lifestep.io) | Inspect XLSX/XLSM structure: sheets, formulas, macros and external links | No | Yes | Yes |

### Dictionaries

| API | 說明 | 驗證 (Auth) | HTTPS | 跨域 (CORS) |
| :--- | :--- | :--- | :--- | :--- |
| [Random Lexicon](https://randomlexicon.com/api-reference) | Random words and definitions using optional filters | No | Yes | Yes |
| [Wiktionary](https://en.wiktionary.org/w/api.php) | Collaborative dictionary data | No | Yes | Yes |
| [WordSoHard](https://wordsohard.com/api) | Word definitions with Scrabble validity and tile score in one call, built for word games | No | Yes | Yes |

### Documents & Productivity

| API | 說明 | 驗證 (Auth) | HTTPS | 跨域 (CORS) |
| :--- | :--- | :--- | :--- | :--- |
| [AgentPay Doc Tools](https://agentpay-tools.agentpay-apis.workers.dev) | PDF to text, RSS/Atom/JSON feeds to JSON and sitemaps to URL lists, paid per call via x402 | No | Yes | Yes |
| [DocStruct](https://docstruct.pages.dev) | AI extraction of invoices, receipts, bank statements & contracts into structured JSON/CSV | No | Yes | Yes |

### Email

| API | 說明 | 驗證 (Auth) | HTTPS | 跨域 (CORS) |
| :--- | :--- | :--- | :--- | :--- |
| [AGPC Domain Check](https://guild.tradeuniquecapital.com/api) | Check a domain's SPF, DKIM, DMARC and MX with a graded shareable report | No | Yes | Yes |
| [Disify](https://www.disify.com/) | Validate and detect disposable and temporary email addresses | No | Yes | Yes |
| [Email Spam Tester](https://email-spam-tester.com/api-docs/) | Send a test message and get a spam score, 41 checks with RFC citations and a fix plan | No | Yes | Yes |
| [Email Validator by LifeStep](https://email.lifestep.io) | Validate email syntax and MX, detect disposable/role addresses, suggest typo fixes | No | Yes | Yes |
| [EVA](https://eva.pingutil.com/) | Validate email addresses | No | Yes | Yes |
| [Kickbox](https://open.kickbox.com/) | Email verification API | No | Yes | Yes |
| [mail.gw](https://docs.mail.gw) | 10 Minute Mail | No | Yes | Yes |
| [mail.tm](https://docs.mail.tm) | Temporary Email Service | No | Yes | Yes |

### Entertainment

| API | 說明 | 驗證 (Auth) | HTTPS | 跨域 (CORS) |
| :--- | :--- | :--- | :--- | :--- |
| [Bucketlist Dream of the Day](https://bucketlist.nl/samenwerken?lang=en#droom-van-de-dag) | Daily travel and life-experience inspiration with canonical links and images | No | Yes | Yes |
| [Corporate Buzz Words](https://github.com/sameerkumar18/corporate-bs-generator-api) | REST API for Corporate Buzz Words | No | Yes | Yes |
| [CosmyDay Astrology](https://cosmyday.com/api-docs) | Natal charts and sky events computed from Swiss Ephemeris | No | Yes | Yes |
| [Fun Fact](https://api.aakhilv.me) | A simple HTTPS api that can randomly select and return a fact from the FFA database | No | Yes | Yes |
| [JokeAPI](https://v2.jokeapi.dev/) | Programmable jokes in multiple languages with filtering options | No | Yes | Yes |
| [justmeme.wtf](https://justmeme.wtf/api-docs) | Free meme API with 2400+ templates, search, trending, and AI generation | No | Yes | Yes |
| [PotterDB](https://docs.potterdb.com/) | Harry Potter universe database with characters, spells, potions and more | No | Yes | Yes |

### Environment

| API | 說明 | 驗證 (Auth) | HTTPS | 跨域 (CORS) |
| :--- | :--- | :--- | :--- | :--- |
| [GrünstromIndex](https://gruenstromindex.de/) | Green Power Index for Germany (Grünstromindex/GSI) | No | No | Yes |
| [kanari](https://kanari.io/en/api) | Real-time worldwide wildfire detections, water bomber tracking and open fire archive | No | Yes | Yes |
| [Open-Meteo](https://open-meteo.com/) | Free weather API for non-commercial use | No | Yes | Yes |
| [WattFigure](https://api.wattfigure.com/) | US electricity rates by state, with appliance and EV charging running costs | No | Yes | Yes |

### Finance

| API | 說明 | 驗證 (Auth) | HTTPS | 跨域 (CORS) |
| :--- | :--- | :--- | :--- | :--- |
| [Banking Access Index](https://www.globalsolo.global/data/banking-access-index) | Which US business banking providers accept founders by country of residence, with sources | No | Yes | Yes |
| [Brainy Prices](https://prices.brainy.ae/developers.html) | UAE living costs: KHDA fees, DLD rents, fuel, utilities, telecom and relocation, with dated sources | No | Yes | Yes |
| [contix](https://contix.es/api/#herramientas) | Spain: IBAN validation with bank and BIC, EU VAT number check (VIES), Modelo 303 VAT sums | No | Yes | Yes |
| [Econdb](https://www.econdb.com/api/) | Global macroeconomic data | No | Yes | Yes |
| [EstimateTax](https://estimatetax.net/api/) | US federal, state and local income tax calculation for 2026, with the source of every figure | No | Yes | Yes |
| [Finance Clearly Tax Rates](https://financeclearly.com/tax-rates-api/) | Current UK and US tax rates, allowances and thresholds | No | Yes | Yes |
| [FloorGuard](https://floorguard-kappa.vercel.app/api/) | Sourced prop firm daily-loss and max-drawdown rules, plus a drawdown-room check | No | Yes | Yes |
| [Futures Clock](https://futuresclock.com/en/data-methodology/#open-data) | Trading hours and session windows for 65 futures products on 16 global exchanges | No | Yes | Yes |
| [Helious](https://helious.io/developers/) | US Treasury auction results with the tail and bidder split, plus scored economic releases | No | Yes | Yes |
| [Helium](https://heliumtrades.com/mcp-page/) | News with media bias scoring, balanced news synthesis, live market data, AI options pricing | No | Yes | Yes |
| [IBAN Analyzer](https://iban-analyzer.com/free-iban-api) | Resolve an IBAN to its bank name, BIC, city and address for 60+ countries | No | Yes | Yes |
| [LiquiLens](https://liquilens.in/developers/) | Public-record bank and lender failure-risk evidence | No | Yes | Yes |
| [PolyKal Fees](https://polymarket-kalshi.com/fee-schedule/) | Kalshi & Polymarket trading fee rates and formulas as verified JSON | No | Yes | Yes |
| [Portfolio Optimizer](https://portfoliooptimizer.io/) | Portfolio analysis and optimization | No | Yes | Yes |
| [SEC EDGAR Data](https://www.sec.gov/edgar/sec-api-documentation) | API to access annual reports of public US companies | No | Yes | Yes |
| [US Mortgage Calculator](https://www.usmortgagecalc.com/developers/api) | Mortgage payment, amortization, affordability and 50-state property tax data | No | Yes | Yes |
| [XOOMAR](https://xoomar.com/markets/api) | US market data from SEC, FINRA, CFTC and the Fed: filings, insiders, earnings dates, short interest | No | Yes | Yes |
| [Zelothorn](https://zelothorn.com/developers) | Plain-English explanations of US public companies with SEC filings and earnings data | No | Yes | Yes |

### Food & Drink

| API | 說明 | 驗證 (Auth) | HTTPS | 跨域 (CORS) |
| :--- | :--- | :--- | :--- | :--- |
| [BaconMockup](https://baconmockup.com/) | Resizable bacon placeholder images | No | Yes | Yes |
| [Daily Food Recalls](https://dailyfoodrecalls.com/api/) | U.S. FDA and USDA food recalls, merged and normalized, updated daily | No | Yes | Yes |
| [ExactCup](https://exactcup.github.io/api/) | Cooking ingredient densities: grams per US cup, tablespoon, teaspoon and mL | No | Yes | Yes |
| [Foodish](https://github.com/surhud004/Foodish#readme) | Random pictures of food dishes | No | Yes | Yes |
| [Open Brewery DB](https://www.openbrewerydb.org) | Breweries, Cideries and Craft Beer Bottle Shops | No | Yes | Yes |
| [Racion](https://racion.app/developers) | Weekly meal plans with grocery prices and shopping lists, 22 countries | No | Yes | Yes |

### Games & Comics

| API | 說明 | 驗證 (Auth) | HTTPS | 跨域 (CORS) |
| :--- | :--- | :--- | :--- | :--- |
| [AmiiboAPI](https://amiiboapi.com/) | Nintendo Amiibo Information | No | Yes | Yes |
| [Astroworld](https://api.astroworldmc.com) | Free Minecraft data: mobs, biomes, items, enchantments, structures, commands, versions, achievements, trades | No | Yes | Yes |
| [Autochess VNG](https://github.com/didadadida93/autochess-vng-api) | Rest Api for Autochess VNG | No | Yes | Yes |
| [Barter.VG](https://github.com/bartervg/barter.vg/wiki) | Provides information about Game, DLC, Bundles, Giveaways, Trading | No | Yes | Yes |
| [Bugsnax](https://www.bugsnaxapi.com/) | Get information about Bugsnax | No | Yes | Yes |
| [CheapShark](https://www.cheapshark.com/api) | Steam/PC Game Prices and Deals | No | Yes | Yes |
| [Crafatar](https://crafatar.com) | API for Minecraft skins and faces | No | Yes | Yes |
| [Cross Universe](https://crossuniverse.psychpsyo.com/apiDocs.html) | Cross Universe Card Data | No | Yes | Yes |
| [Disney](https://disneyapi.dev) | Information of Disney characters | No | Yes | Yes |
| [DotaSense Timings](https://dotasense.com/cheat-sheet#timing-api) | Reviewed Dota 2 objective timings in JSON and CSV | No | Yes | Yes |
| [Dungeons and Dragons (Alternate)](https://open5e.com/) | Includes all monsters and spells from the SRD (System Reference Document) as well as a search API | No | Yes | Yes |
| [FFXIV Collect](https://ffxivcollect.com/) | Final Fantasy XIV data on collectables | No | Yes | Yes |
| [Final Fantasy XIV](https://xivapi.com/) | Final Fantasy XIV Game data API | No | Yes | Yes |
| [FreeToGame](https://www.freetogame.com/api-doc) | Free-To-Play Games Database | No | Yes | Yes |
| [Fun Facts](https://asli-fun-fact-api.herokuapp.com/) | Random Fun Facts | No | Yes | Yes |
| [FunTranslations](https://api.funtranslations.com/) | Translate Text into funny languages | No | Yes | Yes |
| [GamerPower](https://www.gamerpower.com/api-read) | Game Giveaways Tracker | No | Yes | Yes |
| [Geek-Jokes](https://github.com/sameerkumar18/geek-joke-api) | Fetch a random geeky/programming related joke for use in all sorts of applications | No | Yes | Yes |
| [Genshin Impact](https://genshin.dev) | Genshin Impact game data | No | Yes | Yes |
| [GraphQL Pokemon](https://github.com/favware/graphql-pokemon) | GraphQL powered Pokemon API. Supports generations 1 through 8 | No | Yes | Yes |
| [GZW Data](https://gzw-data.vercel.app/docs/) | Gray Zone Warfare weapons, missions, loot, armor and game data | No | Yes | Yes |
| [JokeAPI](https://sv443.net/jokeapi/v2/) | Programming, Miscellaneous and Dark Jokes | No | Yes | Yes |
| [L2 Calendar](https://l2calendar.com/api/servers) | Lineage 2 private servers list with names, websites, chronicles, rates and opening dates | No | Yes | Yes |
| [Monster Hunter World](https://docs.mhw-db.com/) | Monster Hunter World data | No | Yes | Yes |
| [PokéAPI (GraphQL)](https://github.com/mazipan/graphql-pokeapi) | The Unofficial GraphQL for PokeAPI | No | Yes | Yes |
| [PokéSprite](https://msikma.github.io/pokesprite/) | Database of Pokémon sprites and icons | No | Yes | Yes |
| [Psychonauts](https://psychonauts-api.netlify.app/) | Psychonauts World Characters Information and PSI Powers | No | Yes | Yes |
| [Puyo Nexus](https://github.com/deltadex7/puyodb-api-deno) | Puyo Puyo information from Puyo Nexus Wiki | No | Yes | Yes |
| [Rblxdb](https://rblxdb.com/developers) | Verified Roblox music codes and decal IDs with live working status | No | Yes | Yes |
| [Rick and Morty](https://rickandmortyapi.com) | All the Rick and Morty information, including images | No | Yes | Yes |
| [RPS 101](https://rps101.pythonanywhere.com/api) | Rock, Paper, Scissors with 101 objects | No | Yes | Yes |
| [Scryfall](https://scryfall.com/docs/api) | Magic: The Gathering database | No | Yes | Yes |
| [SeedFinder](https://mineseedfinder.vercel.app/seedfinder) | Minecraft Bedrock structures prediction | No | Yes | Yes |
| [SteamGPT](https://steamgpt.net) | Steam profiles, SteamID conversion, VAC/game bans, FACEIT stats and friends | No | Yes | Yes |
| [TCGdex](https://www.tcgdex.net/docs) | Multi languages Pokémon TCG Information | No | Yes | Yes |
| [Universalis](https://universalis.app/docs/index.html) | Final Fantasy XIV market board data | No | Yes | Yes |
| [Worth the Rip](https://worththerip.com/api/) | Sealed trading-card product prices and expected value across 10 TCGs, refreshed every 2 hours | No | Yes | Yes |

### Geocoding

| API | 說明 | 驗證 (Auth) | HTTPS | 跨域 (CORS) |
| :--- | :--- | :--- | :--- | :--- |
| [administrative-divisons-db](https://github.com/kamikazechaser/administrative-divisions-db) | Get all administrative divisions of a country | No | Yes | Yes |
| [bng2latlong](https://www.getthedata.com/bng2latlong) | Convert British OSGB36 easting and northing (British National Grid) to WGS84 latitude and longitude | No | Yes | Yes |
| [Country](http://country.is/) | Get your visitor's country from their IP | No | Yes | Yes |
| [GeographQL](https://geographql.netlify.app) | A Country, State, and City GraphQL API | No | Yes | Yes |
| [GeoJS](https://www.geojs.io/) | IP geolocation with ChatOps integration | No | Yes | Yes |
| [Geokeo](https://geokeo.com) | Geokeo geocoding service- with 2500 free api requests daily | No | Yes | Yes |
| [geoPlugin](https://www.geoplugin.com) | IP geolocation and currency conversion | No | Yes | Yes |
| [HackMyIP](https://hackmyip.com/api) | IP geolocation, ISP and privacy/VPN scoring, email breach checks, DNS and WHOIS lookups | No | Yes | Yes |
| [IP99](https://ip99.com/api) | IP geolocation with proxy, VPN and datacenter risk and the age of the evidence | No | Yes | Yes |
| [ipapi.co](https://ipapi.co/api/#introduction) | Find IP address location information | No | Yes | Yes |
| [ipgeolocationapi](https://ipgeolocationapi.io/docs) | IP geolocation with ASN, timezone, currency and threat data, 5,000 keyless calls a day | No | Yes | Yes |
| [ipwhois](https://ipwhois.io/documentation) | IP geolocation with country, city, coordinates, ISP, timezone and flag data | No | Yes | Yes |
| [LatLng](https://www.latlng.work/docs) | Geocoding, reverse geocoding, places, and static maps | No | Yes | Yes |
| [Moradas](https://moradas.dev/docs) | Portuguese address autocomplete and 7-digit postal codes (CP7) | No | Yes | Yes |
| [Nominatim](https://nominatim.org/release-docs/latest/api/Overview/) | Provides worldwide forward / reverse geocoding | No | Yes | Yes |
| [Pinball Map](https://pinballmap.com/api/v1/docs) | A crowdsourced map of public pinball machines | No | Yes | Yes |
| [Postali](https://postali.app/api) | Mexico Zip Codes API | No | Yes | Yes |
| [Postcodes.io](https://postcodes.io) | Postcode lookup & Geolocation for the UK | No | Yes | Yes |
| [REST Countries](https://restcountries.com) | Get information about countries via a RESTful API | No | Yes | Yes |
| [SearchPinCode](https://searchpincode.in/api) | Indian postal PIN code lookup, post office locator and district data | No | Yes | Yes |
| [SLF](https://github.com/slftool/slftool.github.io/blob/master/API.md) | German city, country, river, database | No | Yes | Yes |
| [Unblock Master IP](https://www.unblockmaster.com/free-ip-api/) | IP geolocation plus datacenter and VPN detection for any IPv4 or IPv6 address | No | Yes | Yes |

### Government

| API | 說明 | 驗證 (Auth) | HTTPS | 跨域 (CORS) |
| :--- | :--- | :--- | :--- | :--- |
| [Ayes and Noes](https://ayesandnoes.co.uk/developers) | UK House of Commons MPs, parties and recorded votes | No | Yes | Yes |
| [Bidledger](https://jaydemks.github.io/bidledger/api.html) | Every open public tender in the European Union, rebuilt daily from the official TED data | No | Yes | Yes |
| [Brazil](https://brasilapi.com.br/) | Community driven API for Brazil Public Data | No | Yes | Yes |
| [City, Toronto Open Data](https://open.toronto.ca/) | Toronto (CA) City Open Data | No | Yes | Yes |
| [ContaCLT](https://contaclt.com/dados/api/) | Brazilian payroll and labor calculations: net salary, INSS, IRRF, unemployment insurance | No | Yes | Yes |
| [EditalMD](https://editalmd.com/api/) | Brazilian public procurement (PNCP) notices as Markdown with deadlines and requirements | No | Yes | Yes |
| [EU VAT Rates by Commodity Code](https://github.com/humora2504/eu-vat-by-commodity-code) | EU VAT rates mapped to CN and CPA commodity codes, all 27 member states | No | Yes | Yes |
| [Indian Mandi Prices](https://mandi-api.vercel.app/docs) | Free, keyless daily wholesale mandi prices for 5 Indian states, sourced from data.gov.in | No | Yes | Yes |
| [Indian Pincode](https://indianpincode.com/) | Free India PIN code lookup with GPS coordinates, 165k+ post offices, state & district data | No | Yes | Yes |
| [LocalGov.jp](https://localgov.jp/) | Japan grants and subsidies (central J-Grants + 1,916 municipalities) | No | Yes | Yes |
| [Open Government, Norway](https://data.norge.no/dataservices) | Norwegian Government Open Data | No | Yes | Yes |
| [Open Government, Poland](https://dane.gov.pl/en) | Poland Government Open Data | No | Yes | Yes |
| [Open Government, Portugal](https://dados.gov.pt/en/recursos/desenvolvimento/referencia-api) | Portugal Government Open Data | No | Yes | Yes |
| [OpenMercantil](https://openmercantil.es/api/documentacion) | Spanish company public data and BORME event timelines | No | Yes | Yes |
| [PRC Exam Schedule](https://api.whenisthenextboardexam.com/docs/) | Unofficial Philippine Professional Regulation Commission's examination schedule | No | Yes | Yes |
| [Right to Disconnect](https://righttodisconnect.jdries.nl/api/) | Right-to-disconnect employment law by EU country: binding status, statute, and sanctions | No | Yes | Yes |
| [Spatial India](https://api.spatialindia.com) | District-level data for India: Census, NFHS-5, NCRB, RBI and more, reconciled onto one map | No | Yes | Yes |
| [Tollmint](https://api.tollmint.com) | Advertising, subscription, AI-disclosure and accessibility rules across the US, EU and UK | No | Yes | Yes |
| [UK Legislation Changes](https://uk-legal-changes.pages.dev/docs) | Point-in-time amendment history for UK law | No | Yes | Yes |
| [US Federal Contracts & Grants](https://government-data-api.onrender.com/docs) | US federal contracts, grants, and agency spending data updated daily | No | Yes | Yes |
| [Veridion](https://www.veridionmarkets.com/data-api/docs) | US congressional stock-trade disclosures and the President's OGE reports, linked to each filing | No | Yes | Yes |
| [Vett](https://wimberly.solutions/api/free-sanctions-check/) | Screen names & companies against OFAC, PEP, watchlists & recalls | No | Yes | Yes |
| [VotePredictor](https://votepredictor.com/developers) | US election forecasts, congressional voting records and forecaster accuracy ratings | No | Yes | Yes |

### Health

| API | 說明 | 驗證 (Auth) | HTTPS | 跨域 (CORS) |
| :--- | :--- | :--- | :--- | :--- |
| [Clinical Trials Directory](https://trials.starfile.org/api) | Every clinical trial registered with ClinicalTrials.gov, indexed by condition and sponsor | No | Yes | Yes |
| [Covid-19](https://covid19api.com/) | Covid 19 spread, infection and recovery | No | Yes | Yes |
| [Covid-19](https://github.com/M-Media-Group/Covid-19-API) | Covid 19 cases, deaths and recovery per country | No | Yes | Yes |
| [Covid-19 Government Response](https://covidtracker.bsg.ox.ac.uk) | Government measures tracker to fight against the Covid-19 pandemic | No | Yes | Yes |
| [Covid-19 JHU CSSE](https://nuttaphat.com/covid19-api/) | Open-source API for exploring Covid19 cases based on JHU CSSE | No | Yes | Yes |
| [Covid-19 Live Data](https://github.com/mathdroid/covid-19-api) | Global and countrywise data of Covid 19 daily Summary, confirmed cases, recovered and deaths | No | Yes | Yes |
| [Covid-19 Philippines](https://github.com/Simperfy/Covid-19-API-Philippines-DOH) | Unofficial Covid-19 Web API for Philippines from data collected by DOH | No | Yes | Yes |
| [COVID-ID](https://data.covid19.go.id/public/api/prov.json) | Indonesian government Covid data per province | No | Yes | Yes |
| [DeepDNA](https://deepdna.ai/docs/) | Cited gene, variant and CPIC drug-gene lookups for developers and AI agents | No | Yes | Yes |
| [FindSaunaPlunge](https://findsaunaplunge.com/api/) | US cold plunge and sauna venues with dated, source-quoted temperatures and prices | No | Yes | Yes |
| [LAPIS](https://cov-spectrum.ethz.ch/public) | SARS-CoV-2 genomic sequences from public sources | No | Yes | Yes |
| [Longevity World Cup](https://longevityworldcup.com/api/data/athletes) | Public biological age competition data with biomarkers and rankings | No | Yes | Yes |
| [Open Disease](https://disease.sh/) | API for Current cases and more stuff about COVID-19 and Influenza | No | Yes | Yes |
| [Quarantine](https://quarantine.country/coronavirus/api/) | Coronavirus API with free COVID-19 live updates | No | Yes | Yes |
| [Urgences Québec](https://sante.handled.tools/api) | Hourly emergency room occupancy, stretcher counts and wait times for every hospital in Quebec, Canada | No | Yes | Yes |

### Jobs

| API | 說明 | 驗證 (Auth) | HTTPS | 跨域 (CORS) |
| :--- | :--- | :--- | :--- | :--- |
| [AI Dev Jobs](https://aidevboard.com/openapi.yaml) | AI/ML engineering job aggregator with REST, RSS, and MCP endpoints | No | Yes | Yes |
| [Arbeitnow](https://documenter.getpostman.com/view/18545278/UVJbJdKh) | API for Job board aggregator in Europe / Remote | No | Yes | Yes |
| [Artificial Intelligence Jobs](https://artificialintelligencejobs.co/developers) | Live AI/ML job listings from 260+ companies' own career pages, with salary, location, remote and seniority filters | No | Yes | Yes |
| [CuratorSearch](https://curatorsearch.com/developers) | Museum and gallery jobs from 400+ institutions' own careers pages, with advertised salaries | No | Yes | Yes |
| [DevITjobs UK](https://devitjobs.uk/job_feed.xml) | Jobs with GraphQL | No | Yes | Yes |
| [GraphQL Jobs](https://graphql.jobs/docs/api/) | Jobs with GraphQL | No | Yes | Yes |
| [RemoteOK](https://remoteok.com/api) | Remote job board for digital nomads | No | Yes | Yes |
| [TechRole Index](https://techrole.ru/open-data-daily) | Russian IT profession, vacancy publication and salary aggregates | No | Yes | Yes |

### Machine Learning

| API | 說明 | 驗證 (Auth) | HTTPS | 跨域 (CORS) |
| :--- | :--- | :--- | :--- | :--- |
| [AI Economics Tools](https://piszczek.pl/tools/api) | Token cost, LLM energy, agent-hour and Proof-Adjusted Autonomy calculators by Michał Piszczek | No | Yes | Yes |
| [DreamThreads](https://mydreamthreads.xyz/dream-interpretation-api) | Parse dreams into structured entities, emotions, agency, threat, and outcomes | No | Yes | Yes |
| [EXUDE-API](http://uttesh.com/exude-api/) | Used for the primary ways for filtering the stopping, stemming words from the text data | No | Yes | Yes |
| [Modelfax](https://bytebrujo.github.io/modelfax/) | LLM pricing, context windows and deprecation dates, schema-validated and updated daily | No | Yes | Yes |
| [Nonobench](https://www.nonobench.com/how-it-works) | Open-source benchmark of how well LLMs solve nonogram puzzles | No | Yes | Yes |
| [Not Human Search](https://nothumansearch.ai/openapi.yaml) | AI tool discovery with agentic scoring for 8,600+ tools and MCP servers | No | Yes | Yes |
| [OpenVisionAPI](https://openvisionapi.com) | Open source computer vision API based on open source models | No | Yes | Yes |
| [Statlyte](https://statlyte.com/api) | Live pricing, context windows and model ids for major LLM APIs | No | Yes | Yes |
| [TensorFeed](https://tensorfeed.ai/developers) | Real-time AI news, model pricing, service status, and agent activity feeds | No | Yes | Yes |

### Music

| API | 說明 | 驗證 (Auth) | HTTPS | 跨域 (CORS) |
| :--- | :--- | :--- | :--- | :--- |
| [Radio Browser](https://api.radio-browser.info/) | List of internet radio stations | No | Yes | Yes |

### News

| API | 說明 | 驗證 (Auth) | HTTPS | 跨域 (CORS) |
| :--- | :--- | :--- | :--- | :--- |
| [Florida Man](https://github.com/juliayxhuang/florida-man-api#readme) | Static JSON dataset of 10,000+ Florida Man headlines by date | No | Yes | Yes |
| [Graphs for Coronavirus](https://corona.dnsforfamily.com/api.txt) | Each Country separately and Worldwide Graphs for Coronavirus. Daily updates | No | Yes | Yes |
| [Noozra](https://noozra.com/api) | Free news headlines from 200+ curated RSS sources | No | Yes | Yes |
| [Spaceflight News](https://spaceflightnewsapi.net) | Spaceflight related news 🚀 | No | Yes | Yes |

### Open Data

| API | 說明 | 驗證 (Auth) | HTTPS | 跨域 (CORS) |
| :--- | :--- | :--- | :--- | :--- |
| [49 Gallery Historical Data](https://api.181649.com/docs) | Normalized historical records and 25 daily-updated reference series | No | Yes | Yes |
| [API Setu](https://www.apisetu.gov.in/) | An Indian Government platform that provides a lot of APIS for KYC, business, education & employment | No | Yes | Yes |
| [Band Atlas](https://www.aiotrf.com/en/ai/band-atlas/developers/) | Cellular IoT bands, 2G/3G sunsets and device compatibility for 46 countries | No | Yes | Yes |
| [Big Data Explained](https://bigdataexplained.com/data) | Cloud data warehouse list prices, read daily from AWS and Azure pricing APIs, with price history | No | Yes | Yes |
| [BTU Graph](https://btugraph.com/data/) | Source-reviewed energy company knowledge graph and directory exports | No | Yes | Yes |
| [CollegeCalcAI](https://collegecalcai.com/developers) | US college admission chance estimates and admissions data for 1,100+ colleges | No | Yes | Yes |
| [CuttingToolsAI](https://cuttingtoolsai.eu/api) | Cross-brand carbide insert grade equivalents by ISO application class | No | Yes | Yes |
| [Edgepedia](https://www.edgechat.ai/developers) | Search and read Edgepedia, a free and growing encyclopedia with citations | No | Yes | Yes |
| [EOSL](https://eosl.ai/api/) | Hardware end-of-sale and end-of-service-life dates by part number, source-linked | No | Yes | Yes |
| [HousingFeed](https://housingfeed.com/docs) | US rental listings from property managers' own websites, verified weekly | No | Yes | Yes |
| [i6eal Open AI Data](https://i6eal.de/en/tools/data/) | Open datasets on AI policy, regulation and public-sector adoption in Germany and the EU | No | Yes | Yes |
| [LottoLens PH](https://remo65588-boop.github.io/lottolens-ph-public-data/api/) | Fixed Philippine PCSO historical results and normal draw schedules | No | Yes | Yes |
| [Microlink.io](https://microlink.io) | Extract structured data from any website | No | Yes | Yes |
| [MostExpensiveWatches](https://mostexpensivewatches.net/api) | Documented luxury watch auction records, live listings, valuations and price indices | No | Yes | Yes |
| [ModelPartFinder Error Codes](https://modelpartfinder.com/docs/api) | Lookup appliance and equipment error codes by brand and code, with recommended replacement parts | No | Yes | Yes |
| [Nobel Prize](https://www.nobelprize.org/about/developer-zone-2/) | Open data about nobel prizes and events | No | Yes | Yes |
| [Open Scholarships](https://scholarships.grudged.io) | Free, openly-licensed directory of US scholarships and student aid from official sources | No | Yes | Yes |
| [OpenSanctions](https://www.opensanctions.org/docs/api/) | Data on international sanctions, crime and politically exposed persons | No | Yes | Yes |
| [PayCrunch](https://paycrunch.co/api.html) | US wages for 1,008 occupations and by state, from BLS OEWS May 2025, static JSON, CC BY 4.0 | No | Yes | Yes |
| [PublicDataHub](https://publicdatahub.org/api) | US public schools, hospitals and federal agency budgets as JSON/CSV, with provenance | No | Yes | Yes |
| [SlashYear](https://slashyear.com/api) | 86,902 historical events as JSON, each quoted from a cited Wikipedia revision | No | Yes | Yes |
| [Statistics of the World](https://statisticsoftheworld.com/api-docs) | Economic data for 218 countries — GDP, population, inflation, and 440+ indicators from IMF and World Bank | No | Yes | Yes |
| [StatOrigin](https://statorigin.org/docs/api) | Industry statistics, each traced to its primary source with a verbatim quote, CC BY 4.0 | No | Yes | Yes |
| [The Deploy Log](https://github.com/dotcomjack/the-deploy-log) | 1,000+ AI deployments, each linked to the publisher's own page, JSON and CSV, CC BY 4.0 | No | Yes | Yes |
| [Tickerz](https://tickerz.com/docs) | Daily indexes of real-world activity from public data, each reading timestamped in Bitcoin | No | Yes | Yes |
| [Tilth](https://www.tilth.uk/data) | Free daily UK fertiliser price index across nine grades, CC BY 4.0 licensed | No | Yes | Yes |
| [Umeå Open Data](https://opendata.umea.se/api/) | Open data of the city Umeå in northen Sweden | No | Yes | Yes |
| [Vuntum](https://vuntum.com/en/api-mcp) | Sourced, dated facts on consumer robots and physical AI, licensed CC BY 4.0 | No | Yes | Yes |
| [Warnely](https://warnely.com/developers) | Composite travel-safety scores for 180 countries (FCDO + US State + GPI + WGI + live incident wire), OpenAPI 3.1 spec, CC BY 4.0 | No | Yes | Yes |

### Open Source Projects

| API | 說明 | 驗證 (Auth) | HTTPS | 跨域 (CORS) |
| :--- | :--- | :--- | :--- | :--- |
| [Evil Insult Generator](https://evilinsult.com/api) | Evil Insults | No | Yes | Yes |
| [GitHub Contribution Chart Generator](https://github-contributions.vercel.app) | Create an image of your GitHub contributions | No | Yes | Yes |
| [GitHub ReadMe Stats](https://github.com/anuraghazra/github-readme-stats) | Add dynamically generated statistics to your GitHub profile ReadMe | No | Yes | Yes |
| [Metabase](https://www.metabase.com/) | An open source Business Intelligence server to share data and analytics inside your company | No | Yes | Yes |
| [Neuronto ARD Registry](https://neuronto.com/api-docs) | Search index of MCP servers, agents and APIs, with the tools each server actually exposes | No | Yes | Yes |

### Personality

| API | 說明 | 驗證 (Auth) | HTTPS | 跨域 (CORS) |
| :--- | :--- | :--- | :--- | :--- |
| [Astro Agents](https://astro-agent.dev/llms.txt) | Deterministic Western and Vedic astrology: natal charts, transits, kundli, dashas, panchang | No | Yes | Yes |
| [Inspiration](https://inspiration.goprogram.ai/docs/) | Motivational and Inspirational quotes | No | Yes | Yes |
| [kanye.rest](https://kanye.rest) | REST API for random Kanye West quotes | No | Yes | Yes |
| [kimiquotes](https://kimiquotes.herokuapp.com/doc) | Team radio and interview quotes by Finnish F1 legend Kimi Räikkönen | No | Yes | Yes |
| [Personality.fyi](https://personality.fyi/api) | Free MBTI personality types and OEJTS test scoring | No | Yes | Yes |
| [PositiveQuotation](https://positivequotation.com/developers/public-domain-quotes-api) | Source-verified public-domain English proverbs with provenance | No | Yes | Yes |
| [quoteclear](https://quoteclear.web.app/) | Ever-growing list of James Clear quotes from the 3-2-1 Newsletter | No | Yes | Yes |
| [Zen Quotes](https://zenquotes.io/) | Large collection of Zen quotes for inspiration | No | Yes | Yes |

### Phone

| API | 說明 | 驗證 (Auth) | HTTPS | 跨域 (CORS) |
| :--- | :--- | :--- | :--- | :--- |
| [Phone Specification](https://github.com/azharimm/phone-specs-api) | Rest Api for Phone specifications | No | Yes | Yes |

### Science & Math

| API | 說明 | 驗證 (Auth) | HTTPS | 跨域 (CORS) |
| :--- | :--- | :--- | :--- | :--- |
| [Botlero](https://botlero.com/api/robots) | Sourced, quoted specs for humanoid robots | No | Yes | Yes |
| [CycleCalcs](https://www.cyclecalcs.com/api.html) | Interpreted astronomy: sun and moon times, moon phases, planets, eclipses, seasons | No | Yes | Yes |
| [DataCite](https://support.datacite.org/docs/rest-api) | Search and retrieve DOI metadata for research datasets and publications | No | Yes | Yes |
| [Europe PMC](https://europepmc.org/RestfulWebService) | Life-science literature search with abstracts, citations and full-text links | No | Yes | Yes |
| [GBIF](https://www.gbif.org/developer/summary) | Global Biodiversity Information Facility | No | Yes | Yes |
| [Launch Library 2](https://thespacedevs.com/llapi) | Spaceflight launches and events database | No | Yes | Yes |
| [MyGene.info](https://docs.mygene.info/) | Gene annotation queries and ID lookup | No | Yes | Yes |
| [Oliver's mTOR Atlas](https://mtor-atlas.org/api/) | Curated mTOR research: studies by evidence type, pathway claims, open questions | No | Yes | Yes |
| [OpenAlex](https://docs.openalex.org/) | Open catalog of scholarly works, authors, institutions, sources, and concepts | No | Yes | Yes |
| [RCSB PDB](https://data.rcsb.org/) | 3D structures of proteins and nucleic acids | No | Yes | Yes |
| [Remote Calc](https://github.com/elizabethadegbaju/remotecalc) | Decodes base64 encoding and parses it to return a solution to the calculation in JSON | No | Yes | Yes |
| [Solar System OpenData](https://api.le-systeme-solaire.net) | Data and facts on solar system bodies and planets | No | Yes | Yes |
| [Tallytopia](https://tallytopia.com/api-docs) | Calculators for finance, health, math, space and sports with step-by-step results | No | Yes | Yes |
| [Unpaywall](https://unpaywall.org/products/api) | Open-access status and legal full-text links for scholarly articles | No | Yes | Yes |
| [xMath](https://x-math.herokuapp.com/) | Random mathematical expressions | No | Yes | Yes |

### Security

| API | 說明 | 驗證 (Auth) | HTTPS | 跨域 (CORS) |
| :--- | :--- | :--- | :--- | :--- |
| [Classify](https://classify-web.herokuapp.com/#/api) | Encrypting & decrypting text messages | No | Yes | Yes |
| [CSR.plus](https://csr.plus/docs/api) | Generate certificate signing requests and private keys without OpenSSL | No | Yes | Yes |
| [dead-drop](https://api.dead-drop.xyz/api/v1/docs) | Ephemeral zero-knowledge encrypted data sharing | No | Yes | Yes |
| [Hashable](https://hashable.space/pages/api/) | A REST API to access high level cryptographic functions and methods | No | Yes | Yes |
| [IPGuardian](https://ipguardian.net/docs) | Check IP addresses against 140+ public threat intelligence blocklists | No | Yes | Yes |
| [IPLogs](https://iplogs.com/docs) | Free VPN, proxy, Tor and datacenter IP detection. 13 sources, active probing | No | Yes | Yes |
| [OSV](https://google.github.io/osv.dev/api/) | Open source vulnerability database and distributed triage infrastructure | No | Yes | Yes |
| [Passwordinator](https://github.com/fawazsullia/password-generator/) | Generate random passwords of varying complexities | No | Yes | Yes |
| [Presend](https://presend.pages.dev/api) | Security and developer utility API -- malware, vulnerability, and domain checks, no signup | No | Yes | Yes |
| [Virushee](https://api.virushee.com/) | Virushee file/data scanning | No | Yes | Yes |
| [VPNDetection](https://docs.vpndetection.io/api) | Check whether an IPv4 or IPv6 address belongs to VPN infrastructure, no key needed | No | Yes | Yes |

### Shopping

| API | 說明 | 驗證 (Auth) | HTTPS | 跨域 (CORS) |
| :--- | :--- | :--- | :--- | :--- |
| [BirkinBagStock](https://birkinbagstock.com/.well-known/openapi.json) | Independent Hermès resale index: inventory, market prices, auction calendar and results | No | Yes | Yes |
| [Marketplace Fee Data](https://www.sellerscalc.com/data) | Seller fee schedules for 21 e-commerce marketplaces and payment processors as JSON | No | Yes | Yes |
| [OneFindMe](https://onefindme.com/mcp) | Search AliExpress in any language: price, rating and orders for the delivery country | No | Yes | Yes |

### Social

| API | 說明 | 驗證 (Auth) | HTTPS | 跨域 (CORS) |
| :--- | :--- | :--- | :--- | :--- |
| [4chan](https://github.com/4chan/4chan-API) | Simple image-based bulletin board dedicated to a variety of topics | No | Yes | Yes |
| [Bluesky](https://docs.bsky.app/) | Decentralized social networking via the AT protocol | No | Yes | Yes |
| [Doge-Meme](https://api.doge-meme.lol/docs) | Top meme posts from r/dogecoin which include 'Meme' flair | No | Yes | Yes |
| [Lanyard](https://github.com/Phineas/lanyard) | Retrieve your presence on Discord through an HTTP REST API or WebSocket | No | Yes | Yes |
| [SwarmMemo](https://swarmmemo.com/protocol.md) | Public bulletin board where AI agents and humans read, post and reply, no account or key needed | No | Yes | Yes |

### Sports & Fitness

| API | 說明 | 驗證 (Auth) | HTTPS | 跨域 (CORS) |
| :--- | :--- | :--- | :--- | :--- |
| [balldontlie](https://www.balldontlie.io) | Balldontlie provides access to stats data from the NBA | No | Yes | Yes |
| [Bet Better](https://betbetter.world/api/) | Sports model win probabilities and fair odds across 13 leagues | No | Yes | Yes |
| [DiscGolf](https://discgolfapi.com/docs/) | Structured disc golf course data | No | Yes | Yes |
| [FanLine Wire](https://fanlinewire.com/docs) | Real-time FanDuel Sportsbook odds — live & in-play and pre-match, with a keyless public snapshot | No | Yes | Yes |
| [Football (Soccer) Videos](https://www.scorebat.com/video-api/) | Embed codes for goals and highlights from Premier League, Bundesliga, Serie A and many more | No | Yes | Yes |
| [Football Standings](https://github.com/azharimm/football-standings-api) | Display football standings e.g epl, la liga, serie a etc. The data is based on espn site | No | Yes | Yes |
| [MoviOdds](https://moviodds.com/doc) | Real-time bet365 soccer odds, every market, pre-match and in-play, over REST and WebSocket | No | Yes | Yes |
| [NoPunt](https://www.nopunt.com/api/picks.json) | Weekly NFL game picks with model win probability, confidence tier and spread | No | Yes | Yes |
| [OddsBench](https://oddsbench.xyz/api/) | Independent monthly latency benchmark of sports odds APIs, with free JSON and CSV data | No | Yes | Yes |
| [Oddsmagnet](https://data.oddsmagnet.com) | Odds history from multiple UK bookmakers | No | Yes | Yes |
| [OpenF1](https://openf1.org/) | Real-time and historical Formula 1 data including laps, car telemetry and positions | No | Yes | Yes |
| [OpenLigaDB](https://www.openligadb.de) | Crowd sourced sports league results | No | Yes | Yes |
| [Padel Snipe](https://padelsnipe.com/fr/world/api) | 4,000+ mapped padel clubs across 9 European countries with GPS and courts | No | Yes | Yes |
| [Sport List & Data](https://developers.decathlon.com/products/sports) | List of and resources related to sports | No | Yes | Yes |
| [SportScore](https://sportscore.com/developers/) | Live scores, fixtures, standings and stats for football, basketball, cricket and tennis | No | Yes | Yes |
| [Squiggle](https://api.squiggle.com.au) | Fixtures, results and predictions for Australian Football League matches | No | Yes | Yes |
| [WhensTheRace](https://whenstherace.com/f1-schedule-json/) | F1 season schedule with UTC session start times as JSON, RSS and iCal | No | Yes | Yes |

### Test Data

| API | 說明 | 驗證 (Auth) | HTTPS | 跨域 (CORS) |
| :--- | :--- | :--- | :--- | :--- |
| [AddressMock](https://addressmock.com/api) | Random US, Hong Kong and Cape Verde addresses with matched city, state and ZIP | No | Yes | Yes |
| [DummyJSON](https://dummyjson.com/) | Fake REST API with products, users, posts, comments, todos and more | No | Yes | Yes |
| [FakerAPI](https://fakerapi.it/en) | APIs collection to get fake data | No | Yes | Yes |
| [flaky](https://flakyapi.dev) | Fake REST API with chaos controls: force any status code, add latency, or a failure rate | No | Yes | Yes |
| [loremfile](https://loremfile.dev/docs/manifest) | Hotlinkable CC0 sample files in 78 formats, each with a SHA-256 in a JSON manifest | No | Yes | Yes |
| [QuickMocker](https://quickmocker.com) | API mocking tool to generate contextual, fake or random data | No | Yes | Yes |
| [Sampuli](https://sampuli.site/api) | Format-true synthetic test data for 90 countries: IDs, IBANs, cards, addresses | No | Yes | Yes |
| [Supercrontab Mock Endpoints](https://supercrontab.com/mock) | Mock endpoints in 8 formats, each returning any of 14 HTTP status codes | No | Yes | Yes |
| [TotalShiftLeft Sandbox](https://demo.totalshiftleft.ai/) | Free multi-protocol sandbox: REST, GraphQL & SOAP with OAuth2/JWT auth and OpenAPI 3.0 spec | No | Yes | Yes |
| [Waldrand Avatar](https://avatar.waldrand.dev) | Deterministic SVG/PNG/WebP avatars from any string, four styles | No | Yes | Yes |
| [What The Commit](http://whatthecommit.com/index.txt) | Random commit message generator | No | No | Yes |

### Transportation

| API | 說明 | 驗證 (Auth) | HTTPS | 跨域 (CORS) |
| :--- | :--- | :--- | :--- | :--- |
| [Apimetro](https://apimetro.dev/swagger/index.html) | Geospatial data for Mexico City public transport system (Metro, Metrobús, Cablebús, RTP, etc.) | No | Yes | Yes |
| [ArcNautical](https://arcnautical.com/developers/) | Screen any ship by IMO for OFAC/EU/UN/UK sanctions, ownership opacity and a vetting grade | No | Yes | Yes |
| [Aviation Safety Data](https://himaxym.com/developers) | 164,068 aircraft accident narratives from 128 official investigation authorities, plus FAA data | No | Yes | Yes |
| [BC Ferries](https://www.bcferriesapi.ca) | Sailing times and capacities for BC Ferries | No | Yes | Yes |
| [Can I enter](https://canienter.com) | Visa and entry requirements for 199 passports, cited to official sources, verified daily | No | Yes | Yes |
| [ChargeAlong](https://chargealong.io/docs/) | EV charging sites in AU, NZ, US, UK and Canada, with nearby search and trip planning | No | Yes | Yes |
| [ConnectMeGuru](https://www.connectmeguru.com/api/mcp) | Search and purchase prepaid travel eSIM data plans across 190+ countries | No | Yes | Yes |
| [FAA N-Number Registry](https://n-number.starfile.org/api) | Every FAA-registered civil aircraft in the United States, lookup by N-number or Mode S hex code | No | Yes | Yes |
| [GTFS Scorecard](https://github.com/ChelseaKR/gtfs-scorecard/blob/main/docs/api.md) | Data-quality grades and prioritized fixes for 2,400+ public transit GTFS feed records | No | Yes | Yes |
| [OpenVan](https://openvan.camp/docs) | Fuel prices for 121 countries, food cost index & vanlife weather scores for RV travel | No | Yes | Yes |
| [Railworks](https://railworks.paddez.com/docs) | Irish Rail planned engineering works: affected stations, DART closures, change log and ICS feeds | No | Yes | Yes |
| [Transport for Belgium](https://docs.irail.be/) | The iRail API is a third-party API for Belgian public transport by train | No | Yes | Yes |
| [transport.rest](https://transport.rest) | Community maintained, developer-friendly public transport API | No | Yes | Yes |

### URL Shorteners

| API | 說明 | 驗證 (Auth) | HTTPS | 跨域 (CORS) |
| :--- | :--- | :--- | :--- | :--- |
| [1pt](https://github.com/1pt-co/api/blob/main/README.md) | A simple URL shortener | No | Yes | Yes |
| [CleanURI](https://cleanuri.com/docs) | URL shortener service | No | Yes | Yes |
| [GoTiny](https://github.com/robvanbakel/gotiny-api) | A lightweight URL shortener, focused on ease-of-use for the developer and end-user | No | Yes | Yes |
| [Shrtcode](https://shrtco.de/docs) | URl Shortener with multiple Domains | No | Yes | Yes |

### Vehicle

| API | 說明 | 驗證 (Auth) | HTTPS | 跨域 (CORS) |
| :--- | :--- | :--- | :--- | :--- |
| [Bike Reliability](https://bikereliability.co.uk/developers) | UK motorcycle reliability ranked by first-time MOT pass rates | No | Yes | Yes |
| [ProblemsByVin](https://problemsbyvin.com/data/) | Owner complaints, recalls and failure-mileage statistics by vehicle make, model and year | No | Yes | Yes |
| [TransparentCars](https://transparent.pt/en/api) | Fair-price valuation and yearly road tax (IUC) for used cars in Portugal | No | Yes | Yes |

### Video

| API | 說明 | 驗證 (Auth) | HTTPS | 跨域 (CORS) |
| :--- | :--- | :--- | :--- | :--- |
| [Bob's Burgers](https://bobs-burgers-api-ui.herokuapp.com) | Bob's Burgers API | No | Yes | Yes |
| [Dune](https://github.com/ywalia01/dune-api) | A simple API which provides you with book, character, movie and quotes JSON data | No | Yes | Yes |
| [Final Space](https://finalspaceapi.com/docs/) | Final Space API | No | Yes | Yes |
| [IMDbOT](https://github.com/SpEcHiDe/IMDbOT) | Unofficial IMDb Movie / Series Information | No | Yes | Yes |
| [MCU Countdown](https://github.com/DiljotSG/MCU-Countdown) | A Countdown to the next MCU Film | No | Yes | Yes |
| [Movie Quote](https://github.com/F4R4N/movie-quote/) | Random Movie and Series Quotes | No | Yes | Yes |
| [Owen Wilson Wow](https://owen-wilson-wow-api.herokuapp.com) | API for actor Owen Wilson's "wow" exclamations in movies | No | Yes | Yes |
| [SWAPI](https://swapi.dev/) | All the Star Wars data you've ever wanted | No | Yes | Yes |
| [SWAPI](https://www.swapi.tech) | All things Star Wars | No | Yes | Yes |
| [UGCdrop](https://ugcdrop.com/api) | Search real UGC video clips (reactions, hooks, b-roll) by emotion, niche, age and setting | No | Yes | Yes |
| [Video to Markdown](https://video-to-markdown.com/api) | Turn a YouTube URL into a markdown thumbnail image link | No | Yes | Yes |
| [Web Series Quotes Generator](https://github.com/yogeshwaran01/web-series-quotes) | API generates various Web Series Quote Images | No | Yes | Yes |

### Weather

| API | 說明 | 驗證 (Auth) | HTTPS | 跨域 (CORS) |
| :--- | :--- | :--- | :--- | :--- |
| [Hail History](https://hail-history-noaa.netlify.app/api-docs.html) | Radar-detected hail history for any US address from NOAA NEXRAD Level-III hail detections, by year | No | Yes | Yes |
| [NASA POWER](https://power.larc.nasa.gov/docs/) | Global solar and weather data for energy and agriculture | No | Yes | Yes |
| [Open-Meteo](https://open-meteo.com/) | Global weather forecast API for non-commercial use | No | Yes | Yes |
| [Open-Meteo Ensemble](https://open-meteo.com/en/docs/ensemble-api) | Weather ensemble forecasts from multiple models | No | Yes | Yes |
| [openSenseMap](https://api.opensensemap.org/) | Data from Personal Weather Stations called senseBoxes | No | Yes | Yes |
| [Pirate Weather](https://pirateweather.net/en/latest/) | Free weather API with forecast data similar to Dark Sky | No | Yes | Yes |
| [Terrace Weather](https://terrace.javiermateo.dev/swagger-ui.html) | Terrace open/closed verdict for restaurants, from the weather forecast | No | Yes | Yes |
| [US Weather](https://www.weather.gov/documentation/services-web-api) | US National Weather Service | No | Yes | Yes |
| [WeatherTotals](https://weathertotals.com/api) | Measured US snow, rain, hail and aurora totals by state and city | No | Yes | Yes |
| [World Time & Weather](https://worldtimeweather.com/api.html) | Current weather, local time, UTC offset and DST rules for 400 cities as static JSON | No | Yes | Yes |
| [wttr.in](https://wttr.in/:help) | Weather in your terminal, supports JSON output | No | Yes | Yes |
