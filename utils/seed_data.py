import os
import re
from PIL import Image, ImageDraw, ImageFont

# 1. Categories definitions (16 categories)
CATEGORIES = [
    {"name": "Electronics", "slug": "electronics", "description": "Smart TVs, Bluetooth speakers, DSLR cameras, and smart devices."},
    {"name": "Fashion", "slug": "fashion", "description": "Designer casual shirts, hoodies, jeans, sarees, and traditional wear."},
    {"name": "Home & Kitchen", "slug": "home-kitchen", "description": "Modern home accessories, dining tables, cookwares, and kitchen electronics."},
    {"name": "Books & Media", "slug": "books-media", "description": "Data science books, business strategy guides, comics, and music albums."},
    {"name": "Sports & Outdoors", "slug": "sports-outdoors", "description": "Cricket bats, footballs, tents, helmets, and hiking accessories."},
    {"name": "Smartphones", "slug": "smartphones", "description": "Latest 5G mobile phones, folding devices and flagships."},
    {"name": "Laptops", "slug": "laptops", "description": "Powerful ultrabooks, gaming laptops and thin-and-light notebooks."},
    {"name": "Footwear", "slug": "footwear", "description": "Premium sneakers, formal leather shoes, sandals, and heels."},
    {"name": "Beauty", "slug": "beauty", "description": "Skin care serums, cosmetics, lotions, and perfumes."},
    {"name": "Gaming", "slug": "gaming", "description": "Consoles, mechanical keyboards, VR headsets, and gaming monitors."},
    {"name": "Groceries", "slug": "groceries", "description": "Premium basmati rice, mustard oil, organic grains, and coffee staples."},
    {"name": "Furniture", "slug": "furniture", "description": "Comfortable sofas, solid wood beds, study desks, and office chairs."},
    {"name": "Fitness", "slug": "fitness", "description": "Home gym dumbbells, natural yoga mats, treadmills, and high-grade protein."},
    {"name": "Books", "slug": "books", "description": "Bestselling self-help, MCA textbooks, and interview prep guides."},
    {"name": "Accessories", "slug": "accessories", "description": "Laptop bags, smart watch straps, charger hubs, and phone covers."},
    {"name": "Appliances", "slug": "appliances", "description": "Smart refrigerators, washing machines, ceiling fans, and geysers."}
]

# 2. Vendor stores definitions (12 vendors)
VENDORS = [
    {"username": "tech_hub", "email": "vendor.techhub@gmail.com", "business_name": "TechHub Electronics", "description": "Premier store for smart home systems, home theater systems, audio devices, and computer gears."},
    {"username": "fashion_world", "email": "vendor.fashionworld@gmail.com", "business_name": "Fashion World", "description": "Your global lifestyle store for trendy clothing, blazers, kurtas, and apparel accessory ranges."},
    {"username": "home_essentials", "email": "vendor.homeessentials@gmail.com", "business_name": "Home Essentials", "description": "Reliable items for comfortable home living: cookwares, air fryers, and cleaning aids."},
    {"username": "book_planet", "email": "vendor.bookplanet@gmail.com", "business_name": "Book Planet", "description": "The universe of books: programming guides, research writeups, textbooks, and fiction novels."},
    {"username": "sports_arena", "email": "vendor.sportsarena@gmail.com", "business_name": "Sports Arena", "description": "Authorized items for sports players, gym weights, tracking gear, and mountain hiking kits."},
    {"username": "mobile_galaxy", "email": "vendor.mobilegalaxy@gmail.com", "business_name": "Mobile Galaxy", "description": "Authorized multi-brand showroom for high-speed 5G mobile phones and premium accessories."},
    {"username": "laptop_zone", "email": "vendor.laptopzone@gmail.com", "business_name": "Laptop Zone", "description": "Expert tech hub for students, content creators, and corporate business notebooks."},
    {"username": "beauty_store", "email": "vendor.beautystore@gmail.com", "business_name": "Beauty Store", "description": "Dermatologist-tested daily skincare, high-definition cosmetic sets, and pleasant perfumes."},
    {"username": "gamers_hub", "email": "vendor.gamershub@gmail.com", "business_name": "Gamer's Hub", "description": "Ultimate zone for elite virtual reality gears, mechanical boards, and custom accessories."},
    {"username": "fresh_mart", "email": "vendor.freshmart@gmail.com", "business_name": "Fresh Mart", "description": "Organically processed grains, pure oils, whole spices, tea blends, and premium dry fruits."},
    {"username": "furniture_palace", "email": "vendor.furniturepalace@gmail.com", "business_name": "Furniture Palace", "description": "Classic and contemporary wood dining tables, sofas, recliners, and headboards."},
    {"username": "fitness_factory", "email": "vendor.fitnessfactory@gmail.com", "business_name": "Fitness Factory", "description": "Premium supplier of power racks, cardio equipment, bands, and health whey protein."}
]

# 3. Product items definitions (8 products per category, 16 categories = 128 products)
PRODUCTS = [
    # Electronics (TechHub Electronics)
    {"category": "Electronics", "vendor": "TechHub Electronics", "name": "Sony Bravia 55-inch 4K Google TV", "price": 57900.00, "stock": 10, "rating": 4.7, "description": "4K Ultra HD Smart LED TV featuring HDR10, Dolby Audio, and Google Assistant voice controls.", "discount": 15},
    {"category": "Electronics", "vendor": "TechHub Electronics", "name": "JBL Flip 6 Waterproof Speaker", "price": 9999.00, "stock": 25, "rating": 4.5, "description": "Portable waterproof bluetooth speaker with 2-way speaker system, booming bass, and 12hr playback.", "discount": 20},
    {"category": "Electronics", "vendor": "TechHub Electronics", "name": "Titan Smart Watch X", "price": 4999.00, "stock": 15, "rating": 4.8, "description": "Premium smart watch with AMOLED screen, GPS tracking, sleep monitor, and 7-day battery life.", "discount": 25, "image_file": "watch.jpg"},
    {"category": "Electronics", "vendor": "TechHub Electronics", "name": "Nexus Pro Wireless Earbuds", "price": 2499.00, "stock": 35, "rating": 4.5, "description": "True wireless earbuds with Active Noise Cancellation (ANC), deep bass driver, and quick-charge case.", "discount": 30, "image_file": "earbuds.jpg"},
    {"category": "Electronics", "vendor": "TechHub Electronics", "name": "Canon EOS 1500D DSLR Camera", "price": 41990.00, "stock": 8, "rating": 4.4, "description": "APS-C CMOS sensor camera with 24.1 megapixels, dual lens kit, and built-in Wi-Fi and NFC.", "discount": 10},
    {"category": "Electronics", "vendor": "TechHub Electronics", "name": "Ambrane 20000mAh Power Bank", "price": 1499.00, "stock": 50, "rating": 4.3, "description": "20W fast charging power bank with dual USB outputs, Type C input, and multi-layer protection.", "discount": 40},
    {"category": "Electronics", "vendor": "TechHub Electronics", "name": "Samsung Galaxy Tab A9+", "price": 18999.00, "stock": 18, "rating": 4.6, "description": "11.0 inch high-definition display tablet, Snapdragon processor, quad speakers, and 64GB storage.", "discount": 12},
    {"category": "Electronics", "vendor": "TechHub Electronics", "name": "LG 24-inch IPS Borderless Monitor", "price": 9499.00, "stock": 12, "rating": 4.5, "description": "Full HD borderless screen monitor with 75Hz refresh rate, AMD FreeSync, and reader mode.", "discount": 18},

    # Fashion (Fashion World)
    {"category": "Fashion", "vendor": "Fashion World", "name": "Roadster Solid Cotton Polo T-Shirt", "price": 599.00, "stock": 100, "rating": 4.2, "description": "Classic solid cotton regular-fit polo t-shirt with ribbed collars and two-button placket.", "discount": 35},
    {"category": "Fashion", "vendor": "Fashion World", "name": "Biba Printed Cotton Straight Kurti", "price": 1499.00, "stock": 45, "rating": 4.4, "description": "Traditional ethnic Indian printed kurti with 3/4th sleeves, keyhole neck, and soft cotton lining.", "discount": 20},
    {"category": "Fashion", "vendor": "Fashion World", "name": "Jack & Jones Overhead Hoodie", "price": 2499.00, "stock": 30, "rating": 4.5, "description": "Cozy pullover fleece-lined cotton blend hoodie with front kangaroo pocket and drawstring hood.", "discount": 40},
    {"category": "Fashion", "vendor": "Fashion World", "name": "Levi's 511 Men's Slim Fit Jeans", "price": 2999.00, "stock": 60, "rating": 4.6, "description": "Modern slim-fit stretch denim jeans with five pockets, belt loops, and signature Levi's patch.", "discount": 30},
    {"category": "Fashion", "vendor": "Fashion World", "name": "Puma Padded Winter Warm Jacket", "price": 4999.00, "stock": 15, "rating": 4.7, "description": "Water-resistant padded winter jacket with full zip, side pockets, and Puma branding on chest.", "discount": 45},
    {"category": "Fashion", "vendor": "Fashion World", "name": "Banarasi Silk Blend Traditional Saree", "price": 3999.00, "stock": 20, "rating": 4.8, "description": "Gorgeous Banarasi silk blend saree decorated with golden zari work, matching unstitched blouse piece.", "discount": 25},
    {"category": "Fashion", "vendor": "Fashion World", "name": "Allen Solly Solid Formal Shirt", "price": 1299.00, "stock": 50, "rating": 4.3, "description": "Sharp cotton-rich formal shirt with regular collar, full sleeves, and clean chest pocket.", "discount": 15},
    {"category": "Fashion", "vendor": "Fashion World", "name": "Lavie Premium Faux Leather Handbag", "price": 1899.00, "stock": 25, "rating": 4.2, "description": "Stylish women's tote handbag with double handles, spacious zip compartments, and metal fittings.", "discount": 30},

    # Home & Kitchen (Home Essentials / Furniture Palace)
    {"category": "Home & Kitchen", "vendor": "Home Essentials", "name": "Prestige Iris 750W Mixer Grinder", "price": 3499.00, "stock": 30, "rating": 4.3, "description": "Powerful 750W motor mixer grinder with 3 stainless steel jars, 1 juice jar, and overload switch.", "discount": 25},
    {"category": "Home & Kitchen", "vendor": "Home Essentials", "name": "Philips Digital Air Fryer 4.1L", "price": 6999.00, "stock": 14, "rating": 4.5, "description": "Rapid Air tech digital air fryer, lets you bake, grill, fry, and roast with up to 90% less oil.", "discount": 20},
    {"category": "Home & Kitchen", "vendor": "Home Essentials", "name": "Bajaj 20L Solo Microwave Oven", "price": 5499.00, "stock": 22, "rating": 4.2, "description": "Solo microwave oven with mechanical knobs, multi-stage cooking power, and auto-defrost feature.", "discount": 15},
    {"category": "Home & Kitchen", "vendor": "Home Essentials", "name": "Pigeon Non-Stick Cookware Set", "price": 1299.00, "stock": 40, "rating": 4.1, "description": "3-piece non-stick cookware set including one kadai, one tawa, and one flat frypan.", "discount": 35},
    {"category": "Home & Kitchen", "vendor": "Furniture Palace", "name": "Solid Wood 4-Seater Dining Table", "price": 18999.00, "stock": 5, "rating": 4.6, "description": "Classic four-seater dining set made of premium sheesham wood in warm honey finish.", "discount": 10},
    {"category": "Home & Kitchen", "vendor": "Home Essentials", "name": "Kent Grand RO Water Purifier", "price": 14999.00, "stock": 15, "rating": 4.6, "description": "Multi-stage RO+UV+UF water purifier with TDS control system and 8L storage tank.", "discount": 18},
    {"category": "Home & Kitchen", "vendor": "Home Essentials", "name": "Panasonic 1.8L Electric Rice Cooker", "price": 2499.00, "stock": 28, "rating": 4.3, "description": "Automatic electric rice cooker with keep-warm function, anodized aluminum pan, and scoop.", "discount": 12},
    {"category": "Home & Kitchen", "vendor": "Home Essentials", "name": "Eureka Forbes Quick Clean Vacuum", "price": 3299.00, "stock": 20, "rating": 4.4, "description": "1200W powerful suction vacuum cleaner with dust bag indicator and automatic cord winder.", "discount": 22},

    # Books & Media (Book Planet)
    {"category": "Books & Media", "vendor": "Book Planet", "name": "Python Crash Course by Matthes", "price": 599.00, "stock": 45, "rating": 4.8, "description": "A hands-on, project-based introduction to programming in Python. Highly recommended for students.", "discount": 10},
    {"category": "Books & Media", "vendor": "Book Planet", "name": "Python Data Science Handbook", "price": 899.00, "stock": 35, "rating": 4.7, "description": "Essential guide to analyzing, cleaning, and visualizing structured data using NumPy, Pandas, and Scikit-Learn.", "discount": 15},
    {"category": "Books & Media", "vendor": "Book Planet", "name": "AI & ML Comprehensive Guide", "price": 1299.00, "stock": 20, "rating": 4.6, "description": "Theoretical and practical foundations of artificial intelligence and machine learning pipelines.", "discount": 20},
    {"category": "Books & Media", "vendor": "Book Planet", "name": "Blue Ocean Strategy Edition", "price": 490.00, "stock": 60, "rating": 4.5, "description": "Bestselling business guide on how to create uncontested market space and make competition irrelevant.", "discount": 12},
    {"category": "Books & Media", "vendor": "Book Planet", "name": "The Alchemist Novel by Coelho", "price": 299.00, "stock": 100, "rating": 4.9, "description": "An inspiring fable about Santiago, an Andalusian shepherd boy who journeys to find worldly treasure.", "discount": 25},
    {"category": "Books & Media", "vendor": "Book Planet", "name": "Marvel Ultimate Spider-Man Comic 1", "price": 199.00, "stock": 80, "rating": 4.3, "description": "The first issue introducing Peter Parker's ultimate origins and his rise as the friendly neighborhood hero.", "discount": 5},
    {"category": "Books & Media", "vendor": "Book Planet", "name": "Coke Studio India Season 1 Audio CD", "price": 349.00, "stock": 25, "rating": 4.4, "description": "Exclusive collection of traditional and fusion music tracks recorded live in Coke Studio India.", "discount": 30},
    {"category": "Books & Media", "vendor": "Book Planet", "name": "National Geographic Kids Magazine", "price": 150.00, "stock": 120, "rating": 4.5, "description": "A fun, colorful educational monthly magazine packed with wild animals and science facts.", "discount": 10},

    # Sports & Outdoors (Sports Arena)
    {"category": "Sports & Outdoors", "vendor": "Sports Arena", "name": "MRF Genius Grand Kashmir Willow Bat", "price": 1899.00, "stock": 15, "rating": 4.5, "description": "High-quality Kashmir Willow cricket bat with premium rubber grip and full cover.", "discount": 15},
    {"category": "Sports & Outdoors", "vendor": "Sports Arena", "name": "Nivia Storm Size 5 Football", "price": 399.00, "stock": 90, "rating": 4.5, "description": "Heavy-duty hand-stitched TPU football, official weight and shape retention.", "discount": 25},
    {"category": "Sports & Outdoors", "vendor": "Sports Arena", "name": "Nike Academy Duffle Gym Bag", "price": 1499.00, "stock": 40, "rating": 4.4, "description": "Spacious duffle gym bag with separate shoe compartment and water-resistant base.", "discount": 20},
    {"category": "Sports & Outdoors", "vendor": "Sports Arena", "name": "Decathlon Mountain Bike Helmet", "price": 1199.00, "stock": 30, "rating": 4.3, "description": "Adjustable bicycling helmet with multiple air vents, soft inner padding, and visor.", "discount": 10},
    {"category": "Sports & Outdoors", "vendor": "Sports Arena", "name": "Boldfit Anti-Slip TPE Yoga Mat", "price": 499.00, "stock": 100, "rating": 4.4, "description": "6mm extra thick yoga mat with carry strap, anti-tear mesh, and sweat-resistant design.", "discount": 30},
    {"category": "Sports & Outdoors", "vendor": "Sports Arena", "name": "Kore 10kg Chrome Dumbbell Set", "price": 1299.00, "stock": 40, "rating": 4.1, "description": "Home gym workout weights set with chrome plates, lock collars, and carrying case.", "discount": 35},
    {"category": "Sports & Outdoors", "vendor": "Sports Arena", "name": "Woodland Leather Hiking Shoes", "price": 3499.00, "stock": 18, "rating": 4.6, "description": "Durable nubuck leather outdoor trekking shoes with high-traction rubber lug grip.", "discount": 15},
    {"category": "Sports & Outdoors", "vendor": "Sports Arena", "name": "Quechua Waterproof Camping Tent", "price": 4999.00, "stock": 8, "rating": 4.7, "description": "Waterproof double-walled dome tent, accommodates up to 3 persons easily.", "discount": 20},

    # Smartphones (Mobile Galaxy)
    {"category": "Smartphones", "vendor": "Mobile Galaxy", "name": "Apple iPhone 15 (128 GB)", "price": 71999.00, "stock": 15, "rating": 4.9, "description": "Super Retina XDR screen, Dynamic Island, A16 Bionic processor, and 48MP main camera.", "discount": 8},
    {"category": "Smartphones", "vendor": "Mobile Galaxy", "name": "Samsung Galaxy S24 Ultra 5G", "price": 129999.00, "stock": 10, "rating": 4.8, "description": "Titanium design, built-in S-Pen, Galaxy AI, and 200MP camera with 100x zoom.", "discount": 5},
    {"category": "Smartphones", "vendor": "Mobile Galaxy", "name": "OnePlus 12 5G (512GB)", "price": 69999.00, "stock": 12, "rating": 4.7, "description": "Snapdragon 8 Gen 3 processor, 16GB RAM, 100W SuperVOOC charging, and Hasselblad camera.", "discount": 10},
    {"category": "Smartphones", "vendor": "Mobile Galaxy", "name": "Redmi Note 13 Pro 5G", "price": 25999.00, "stock": 25, "rating": 4.4, "description": "1.5K AMOLED 120Hz display, 200MP camera with OIS, and 67W turbo charging.", "discount": 15},
    {"category": "Smartphones", "vendor": "Mobile Galaxy", "name": "Realme Narzo 60 Pro 5G", "price": 21999.00, "stock": 30, "rating": 4.3, "description": "Premium vegan leather back design, 120Hz curved display, and 100MP camera.", "discount": 18},
    {"category": "Smartphones", "vendor": "Mobile Galaxy", "name": "Vivo V30 Pro 5G", "price": 41999.00, "stock": 14, "rating": 4.6, "description": "Professional portrait studio with Zeiss optics, aura light system, and super-slim body.", "discount": 12},
    {"category": "Smartphones", "vendor": "Mobile Galaxy", "name": "Oppo Reno 11 Pro 5G", "price": 37999.00, "stock": 16, "rating": 4.5, "description": "MediaTek Dimensity 8200 processor, 80W flash charging, and ultra-clear portrait system.", "discount": 10},
    {"category": "Smartphones", "vendor": "Mobile Galaxy", "name": "Google Pixel 8 (128 GB)", "price": 62999.00, "stock": 8, "rating": 4.7, "description": "Google Tensor G3 chip, advanced Pixel photography, and 7 years of direct OS updates.", "discount": 10},

    # Laptops (Laptop Zone)
    {"category": "Laptops", "vendor": "Laptop Zone", "name": "Apple MacBook Air Laptop M3", "price": 104900.00, "stock": 8, "rating": 4.9, "description": "Ultra-thin aluminum chassis, M3 silicon processor, liquid retina display, up to 18hr battery.", "discount": 5},
    {"category": "Laptops", "vendor": "Laptop Zone", "name": "Dell XPS 13 Plus Laptop", "price": 144990.00, "stock": 5, "rating": 4.8, "description": "Borderless UHD+ InfinityEdge display, Core i7 processor, 16GB RAM, and haptic touch trackpad.", "discount": 8},
    {"category": "Laptops", "vendor": "Laptop Zone", "name": "HP Pavilion 14 Ryzen 5 Laptop", "price": 54990.00, "stock": 20, "rating": 4.4, "description": "Compact metal keyboard panel notebook, AMD Ryzen 5, 16GB RAM, back-lit keyboard.", "discount": 15},
    {"category": "Laptops", "vendor": "Laptop Zone", "name": "Lenovo Legion 5 Gaming Laptop", "price": 89990.00, "stock": 10, "rating": 4.6, "description": "High-tier gaming notebook, Ryzen 7 processor, RTX 4050 GPU, 144Hz high refresh screen.", "discount": 18},
    {"category": "Laptops", "vendor": "Laptop Zone", "name": "ASUS ROG Strix G16 Core i9", "price": 139990.00, "stock": 6, "rating": 4.8, "description": "Heavy gaming system with Core i9 13th Gen, RTX 4060, ROG intelligent liquid cooling system.", "discount": 12},
    {"category": "Laptops", "vendor": "Laptop Zone", "name": "Acer Aspire Lite Ryzen 3", "price": 27990.00, "stock": 25, "rating": 4.1, "description": "Affordable daily laptop with AMD Ryzen 3, 8GB RAM, and 512GB SSD storage.", "discount": 20},
    {"category": "Laptops", "vendor": "Laptop Zone", "name": "MSI Cyborg 15 Core i5 RTX 4050", "price": 64990.00, "stock": 14, "rating": 4.5, "description": "Translucent lightweight cyberpunk design gaming notebook, Intel i5, RTX 4050.", "discount": 22},
    {"category": "Laptops", "vendor": "Laptop Zone", "name": "Samsung Galaxy Book4 i5 Laptop", "price": 74990.00, "stock": 12, "rating": 4.5, "description": "Premium aluminum body laptop, Core i5 processor, AMOLED display, Galaxy Ecosystem sync.", "discount": 10},

    # Footwear (Fashion World)
    {"category": "Footwear", "vendor": "Fashion World", "name": "Puma Firefly Running Shoes", "price": 2499.00, "stock": 40, "rating": 4.3, "description": "Lightweight mesh upper running shoes with cushioned foam midsole and rubber grip.", "discount": 30},
    {"category": "Footwear", "vendor": "Fashion World", "name": "Nike Court Vision Low Sneakers", "price": 5495.00, "stock": 20, "rating": 4.6, "description": "Retro basketball style sneakers with leather upper and classic cupsole support.", "discount": 15},
    {"category": "Footwear", "vendor": "Fashion World", "name": "Bata Comfort Daily Wear Sandals", "price": 799.00, "stock": 70, "rating": 4.1, "description": "Super soft cushioned daily wear sandals with velcro straps and anti-slip sole.", "discount": 20},
    {"category": "Footwear", "vendor": "Fashion World", "name": "Red Tape Leather Oxford Shoes", "price": 1899.00, "stock": 50, "rating": 4.2, "description": "Classic premium leather dress oxford shoes, perfect for office and formal weddings.", "discount": 45},
    {"category": "Footwear", "vendor": "Fashion World", "name": "Woodland Leather High Top Boots", "price": 3999.00, "stock": 18, "rating": 4.5, "description": "Sturdy nubuck leather high top ankle boots, slip-resistant deep groove outdoor soles.", "discount": 25},
    {"category": "Footwear", "vendor": "Fashion World", "name": "Adidas Ultraboost Light Shoes", "price": 14999.00, "stock": 12, "rating": 4.8, "description": "Top-tier running shoes with high energy return boost midsoles and Primeknit upper.", "discount": 15},
    {"category": "Footwear", "vendor": "Fashion World", "name": "Catwalk Block Heel Sandals", "price": 1499.00, "stock": 30, "rating": 4.2, "description": "Chic women's dress wear sandals with supportive block heels and secure straps.", "discount": 35},
    {"category": "Footwear", "vendor": "Fashion World", "name": "Crocs Classic Unisex Slippers", "price": 2495.00, "stock": 45, "rating": 4.5, "description": "Waterproof comfort clogs/slippers with pivoting heel straps and custom styling ports.", "discount": 10},

    # Beauty (Beauty Store)
    {"category": "Beauty", "vendor": "Beauty Store", "name": "Himalaya Purifying Neem Face Wash", "price": 199.00, "stock": 100, "rating": 4.4, "description": "Clinically proven neem face wash to clean impurities and reduce pimples naturally.", "discount": 10},
    {"category": "Beauty", "vendor": "Beauty Store", "name": "Maybelline Superstay Matte Lipstick", "price": 349.00, "stock": 80, "rating": 4.3, "description": "Transfer-proof 16-hour wear liquid matte lipstick in intense Indian red shades.", "discount": 15},
    {"category": "Beauty", "vendor": "Beauty Store", "name": "Fogg Impressio Scent for Men", "price": 499.00, "stock": 60, "rating": 4.2, "description": "Long lasting premium perfume body spray, masculine woody fragrance, 100ml pack.", "discount": 20},
    {"category": "Beauty", "vendor": "Beauty Store", "name": "Nivea Soft Light Moisturiser 200ml", "price": 279.00, "stock": 70, "rating": 4.4, "description": "Non-greasy quick absorbing daily skin cream enriched with Vitamin E and Jojoba oil.", "discount": 15},
    {"category": "Beauty", "vendor": "Beauty Store", "name": "Philips 1200W Foldable Hair Dryer", "price": 999.00, "stock": 40, "rating": 4.3, "description": "Compact foldable hair dryer with two speed settings and gentle air flow nozzle.", "discount": 25},
    {"category": "Beauty", "vendor": "Beauty Store", "name": "Lakme Absolute Perfect Makeup Kit", "price": 1499.00, "stock": 30, "rating": 4.5, "description": "All-in-one makeup gift box containing primer, foundation, eyeliner, and nail polish.", "discount": 30},
    {"category": "Beauty", "vendor": "Beauty Store", "name": "The Derma Co 1% Hyaluronic Sunscreen", "price": 449.00, "stock": 50, "rating": 4.6, "description": "Ultra light aqua gel SPF 50 PA++++ sunscreen. No white cast, non-greasy formula.", "discount": 10},
    {"category": "Beauty", "vendor": "Beauty Store", "name": "L'Oreal Total Repair 5 Shampoo", "price": 599.00, "stock": 65, "rating": 4.4, "description": "650ml hair restoring shampoo with Ceramide-Cement technology to fight 5 signs of damage.", "discount": 20},

    # Gaming (Gamer's Hub)
    {"category": "Gaming", "vendor": "Gamer's Hub", "name": "Sony PlayStation 5 Slim Console", "price": 44990.00, "stock": 8, "rating": 4.9, "description": "Slim version console with high speed SSD, 3D audio, 4K gaming, and DualSense triggers.", "discount": 10},
    {"category": "Gaming", "vendor": "Gamer's Hub", "name": "Xbox Wireless Controller Black", "price": 5390.00, "stock": 25, "rating": 4.7, "description": "Ergonomic controller featuring hybrid D-pad, textured grip, and bluetooth connection.", "discount": 12},
    {"category": "Gaming", "vendor": "Gamer's Hub", "name": "Razer DeathAdder Wired Mouse", "price": 1299.00, "stock": 40, "rating": 4.4, "description": "Ergonomic gaming mouse with 6400 DPI optical sensor and 5 programmable buttons.", "discount": 35},
    {"category": "Gaming", "vendor": "Gamer's Hub", "name": "Redgear Shadow Blade Keyboard", "price": 2499.00, "stock": 30, "rating": 4.4, "description": "Full mechanical keyboard with clicky blue switches, rainbow LED backlit, and control dial.", "discount": 40},
    {"category": "Gaming", "vendor": "Gamer's Hub", "name": "Green Soul Monster Gaming Chair", "price": 14990.00, "stock": 10, "rating": 4.6, "description": "Ergonomic gaming chair with high back, mold foam padding, and adjustable armrests.", "discount": 25},
    {"category": "Gaming", "vendor": "Gamer's Hub", "name": "Meta Quest 3 VR Headset 128GB", "price": 49990.00, "stock": 5, "rating": 4.8, "description": "Advanced mixed reality headset with dual display resolution and spatial audio triggers.", "discount": 5},
    {"category": "Gaming", "vendor": "Gamer's Hub", "name": "Acer Nitro 27 Curved Gaming Monitor", "price": 13999.00, "stock": 15, "rating": 4.5, "description": "1500R curved 165Hz high refresh monitor with AMD FreeSync Premium and 1ms response.", "discount": 30},
    {"category": "Gaming", "vendor": "Gamer's Hub", "name": "ASUS TUF Gaming F15 Laptop", "price": 54990.00, "stock": 12, "rating": 4.6, "description": "Military grade gaming laptop, Intel i5 11th Gen, GTX 1650, 144Hz screen panel.", "discount": 15},

    # Groceries (Fresh Mart)
    {"category": "Groceries", "vendor": "Fresh Mart", "name": "Daawat Rozana Basmati Rice 5kg", "price": 379.00, "stock": 150, "rating": 4.3, "description": "Fragrant and fluffy basmati rice, suitable for delicious everyday cooking.", "discount": 20},
    {"category": "Groceries", "vendor": "Fresh Mart", "name": "Aashirvaad Shudh Chakki Atta 10kg", "price": 460.00, "stock": 120, "rating": 4.6, "description": "100% stone-ground whole wheat flour. Soft rotis guaranteed with dietary fiber.", "discount": 10},
    {"category": "Groceries", "vendor": "Fresh Mart", "name": "Fortune Soya Refined Oil 5L", "price": 649.00, "stock": 100, "rating": 4.4, "description": "Refined soyabean health oil containing Omega 3 fatty acids, ideal for frying.", "discount": 15},
    {"category": "Groceries", "vendor": "Fresh Mart", "name": "Brooke Bond Red Label Tea 1kg", "price": 320.00, "stock": 90, "rating": 4.5, "description": "Assam black tea leaves blend, delivering classic color, taste and strength.", "discount": 12},
    {"category": "Groceries", "vendor": "Fresh Mart", "name": "Nescafe Classic Coffee 200g", "price": 385.00, "stock": 80, "rating": 4.5, "description": "Rich and refreshing instant coffee powder blend made of robusta and arabica beans.", "discount": 8},
    {"category": "Groceries", "vendor": "Fresh Mart", "name": "Haldiram's Nagpur Bhujia Sev 1kg", "price": 249.00, "stock": 110, "rating": 4.4, "description": "Crispy and spicy gram flour fried noodle snack, classic tea-time side item.", "discount": 18},
    {"category": "Groceries", "vendor": "Fresh Mart", "name": "Cadbury Dairy Milk Silk Bar 150g", "price": 175.00, "stock": 200, "rating": 4.7, "description": "Indulgent smooth milk chocolate bar, melts easily in the mouth. Premium gift.", "discount": 10},
    {"category": "Groceries", "vendor": "Fresh Mart", "name": "Happilo California Almonds 500g", "price": 449.00, "stock": 60, "rating": 4.6, "description": "Premium raw California almonds. Rich source of protein and heart-healthy fats.", "discount": 25},

    # Furniture (Furniture Palace)
    {"category": "Furniture", "vendor": "Furniture Palace", "name": "Sleepyhead 3-Seater Wooden Sofa", "price": 13999.00, "stock": 6, "rating": 4.5, "description": "Modern solid wood frame 3-seater sofa with high density foam and gray fabric.", "discount": 25},
    {"category": "Furniture", "vendor": "Furniture Palace", "name": "Wipro Ergonomic Mesh Office Chair", "price": 6999.00, "stock": 15, "rating": 4.6, "description": "Ergonomic mesh-back desk chair with lumbar support, adjustable height and gas lift.", "discount": 30},
    {"category": "Furniture", "vendor": "Furniture Palace", "name": "Wakefit Wood Queen Size Bed", "price": 10499.00, "stock": 8, "rating": 4.4, "description": "Queen size platform bed made of engineered wood, spacious storage compartments in headboard.", "discount": 20},
    {"category": "Furniture", "vendor": "Furniture Palace", "name": "DeckUp Giona Study Table Desk", "price": 3199.00, "stock": 20, "rating": 4.2, "description": "Engineered wood study desk with multiple drawers, modern keyboard tray and shelving.", "discount": 35},
    {"category": "Furniture", "vendor": "Furniture Palace", "name": "Home Centre 3-Door Wardrobe", "price": 12999.00, "stock": 5, "rating": 4.5, "description": "Spacious three-door clothing wardrobe with hanging rods, locker drawers, and vanity mirror.", "discount": 15},
    {"category": "Furniture", "vendor": "Furniture Palace", "name": "Bluewud Wall Mounted TV Unit", "price": 2899.00, "stock": 18, "rating": 4.3, "description": "Sleek wall mounted floating media console with wire management holes and shelf slots.", "discount": 40},
    {"category": "Furniture", "vendor": "Furniture Palace", "name": "Nilkamal Wood 5-Shelf Book Rack", "price": 3499.00, "stock": 12, "rating": 4.1, "description": "Classic 5-shelf bookshelf made of engineered wood, perfect for home libraries.", "discount": 10},
    {"category": "Furniture", "vendor": "Furniture Palace", "name": "The Sleep Company Manual Recliner", "price": 19999.00, "stock": 4, "rating": 4.7, "description": "Manual recliner with SmartGRID tech padding, soft armrests, and 3 level footrest angles.", "discount": 20},

    # Fitness (Fitness Factory)
    {"category": "Fitness", "vendor": "Fitness Factory", "name": "PowerMax TD-M1 Home Treadmill", "price": 21990.00, "stock": 8, "rating": 4.5, "description": "Motorized running machine for home workouts, LCD monitor, foldable with speakers.", "discount": 35},
    {"category": "Fitness", "vendor": "Fitness Factory", "name": "Rubx Hex Dumbbells Set 10kg", "price": 1899.00, "stock": 35, "rating": 4.6, "description": "Two 5kg rubber coated hex dumbbells, steel handle grips for muscle building.", "discount": 25},
    {"category": "Fitness", "vendor": "Fitness Factory", "name": "Boldfit Resistance Band Set of 5", "price": 599.00, "stock": 120, "rating": 4.4, "description": "Five stackable exercise loop bands with varying weight resistance, carry bag included.", "discount": 30},
    {"category": "Fitness", "vendor": "Fitness Factory", "name": "Reach Air Bike Exerciser Cycle", "price": 6299.00, "stock": 15, "rating": 4.2, "description": "Indoor dual action exercise fitness cycle with adjustable resistance and screen tracker.", "discount": 15},
    {"category": "Fitness", "vendor": "Fitness Factory", "name": "MuscleBlaze Biozyme Whey Protein", "price": 3299.00, "stock": 50, "rating": 4.7, "description": "1kg whey isolate powder with clinically tested absorption formula, rich chocolate.", "discount": 10},
    {"category": "Fitness", "vendor": "Fitness Factory", "name": "Xiaomi Redmi Smart Band 2", "price": 1999.00, "stock": 40, "rating": 4.4, "description": "Vivid smart fitness tracker with heart rate, blood oxygen logging, and 14-day battery.", "discount": 20},
    {"category": "Fitness", "vendor": "Fitness Factory", "name": "Adidas Padded Gym Workout Gloves", "price": 799.00, "stock": 60, "rating": 4.3, "description": "Padded mesh-back weightlifting gloves with wrist wrap support and anti-slip palms.", "discount": 35},
    {"category": "Fitness", "vendor": "Fitness Factory", "name": "Decathlon Anti-Burst Yoga Ball", "price": 699.00, "stock": 45, "rating": 4.4, "description": "Anti-burst gymnastics yoga ball, perfect for balance exercises and core training.", "discount": 12},

    # Books (Book Planet)
    {"category": "Books", "vendor": "Book Planet", "name": "Advanced Database Management Systems", "price": 499.00, "stock": 50, "rating": 4.6, "description": "University textbook on database indexing, transaction models, and query optimization.", "discount": 10},
    {"category": "Books", "vendor": "Book Planet", "name": "Database System Concepts by Korth", "price": 750.00, "stock": 40, "rating": 4.7, "description": "Comprehensive theoretical book covering SQL, relational schemas, storage, and recovery.", "discount": 15},
    {"category": "Books", "vendor": "Book Planet", "name": "Operating System Principles Galvin", "price": 690.00, "stock": 45, "rating": 4.5, "description": "Must-have academic print covering CPU scheduling, threads, virtual memory, and security.", "discount": 12},
    {"category": "Books", "vendor": "Book Planet", "name": "Artificial Intelligence Modern Text", "price": 950.00, "stock": 25, "rating": 4.8, "description": "The definitive book by Russell & Norvig detailing heuristic search, logic, and planning.", "discount": 20},
    {"category": "Books", "vendor": "Book Planet", "name": "HTML CSS JS Modern Guide", "price": 399.00, "stock": 65, "rating": 4.4, "description": "Step-by-step tutorial guide on building web layouts using frontend languages.", "discount": 25},
    {"category": "Books", "vendor": "Book Planet", "name": "Cracking the Coding Interview Book", "price": 599.00, "stock": 90, "rating": 4.9, "description": "189 programming questions and solutions on algorithms, structures, and systems.", "discount": 10},
    {"category": "Books", "vendor": "Book Planet", "name": "Quantitative Aptitude R S Aggarwal", "price": 450.00, "stock": 100, "rating": 4.7, "description": "Bestselling preparation book for competitive exams and campus placement processes.", "discount": 18},
    {"category": "Books", "vendor": "Book Planet", "name": "Cloud Computing Architecture Book", "price": 890.00, "stock": 30, "rating": 4.6, "description": "Technical book on SaaS/PaaS models, hypervisors, cloud storage, and security architectures.", "discount": 15},

    # Accessories (Laptop Zone / Mobile Galaxy / TechHub Electronics / Fitness Factory)
    {"category": "Accessories", "vendor": "Laptop Zone", "name": "Lenovo Casual 15.6 Laptop Bag", "price": 899.00, "stock": 45, "rating": 4.3, "description": "Water-repellent polyester laptop backpack with spacious sections and padded straps.", "discount": 40},
    {"category": "Accessories", "vendor": "Mobile Galaxy", "name": "Spigen Rugged Case for iPhone 15", "price": 1199.00, "stock": 50, "rating": 4.6, "description": "Shock-absorption flexible TPU case with spiderweb interior and air cushion technology.", "discount": 15},
    {"category": "Accessories", "vendor": "Fitness Factory", "name": "Soft Silicone Smart Watch Strap", "price": 399.00, "stock": 70, "rating": 4.2, "description": "Soft sweatproof silicone quick-release watch strap, compatible with 22mm lugs.", "discount": 50},
    {"category": "Accessories", "vendor": "TechHub Electronics", "name": "TP-Link USB 3.0 4-Port Hub", "price": 999.00, "stock": 40, "rating": 4.4, "description": "Super slim lightweight 4-port USB splitter hub, plug-and-play high data speeds.", "discount": 30},
    {"category": "Accessories", "vendor": "TechHub Electronics", "name": "Silicone Keyboard Cover Skin", "price": 249.00, "stock": 90, "rating": 4.1, "description": "Thin washable silicone keyboard dust protector skin for standard notebooks.", "discount": 50},
    {"category": "Accessories", "vendor": "Mobile Galaxy", "name": "Elago Universal Aluminum Phone Stand", "price": 699.00, "stock": 35, "rating": 4.3, "description": "Minimalist premium aluminum desktop phone holder with silicone pads.", "discount": 30},
    {"category": "Accessories", "vendor": "TechHub Electronics", "name": "Mi 33W SonicCharge 2.0 Charger", "price": 899.00, "stock": 60, "rating": 4.5, "description": "High-speed charger combo with Type C cable. Supports 33W phone fast-charging.", "discount": 20},
    {"category": "Accessories", "vendor": "TechHub Electronics", "name": "TP-Link Bluetooth 5.0 USB Adapter", "price": 499.00, "stock": 80, "rating": 4.4, "description": "Nano size USB adapter supporting high-speed Bluetooth 5.0 connections on PCs.", "discount": 25},

    # Appliances (Home Essentials)
    {"category": "Appliances", "vendor": "Home Essentials", "name": "Smart Thermostat Hub", "price": 5999.00, "stock": 0, "rating": 4.2, "description": "Smart home climate hub supporting voice control and energy optimization schedules.", "discount": 10, "image_file": "thermostat.jpg"},
    {"category": "Appliances", "vendor": "Home Essentials", "name": "Samsung 236L Double Door Refrigerator", "price": 24990.00, "stock": 6, "rating": 4.6, "description": "Inverter technology frost-free double door fridge with uniform cooling vents.", "discount": 15},
    {"category": "Appliances", "vendor": "Home Essentials", "name": "LG 7kg Front Load Washing Machine", "price": 28990.00, "stock": 10, "rating": 4.5, "description": "Fully automatic washing machine with smart inverter, steam cycles and turbo wash.", "discount": 18},
    {"category": "Appliances", "vendor": "Home Essentials", "name": "Daikin 1.5 Ton 5 Star Inverter AC", "price": 44990.00, "stock": 8, "rating": 4.7, "description": "High-efficiency split inverter AC with stabilizer-free operation and PM2.5 filter.", "discount": 20},
    {"category": "Appliances", "vendor": "Home Essentials", "name": "Crompton SilentPro Ceiling Fan", "price": 3499.00, "stock": 25, "rating": 4.4, "description": "High air delivery energy-efficient BLDC ceiling fan with remote control.", "discount": 30},
    {"category": "Appliances", "vendor": "Home Essentials", "name": "Havells Adonia 25L Storage Geyser", "price": 11999.00, "stock": 12, "rating": 4.6, "description": "Rustproof storage geyser with digital temperature panel and glass-coated element.", "discount": 25},
    {"category": "Appliances", "vendor": "Home Essentials", "name": "Prestige Induction Cooktop 2000W", "price": 2899.00, "stock": 20, "rating": 4.2, "description": "Induction cooktop with pre-programmed Indian menu buttons, automatic voltage control.", "discount": 35},
    {"category": "Appliances", "vendor": "Home Essentials", "name": "Symphony Diet 12T Tower Air Cooler", "price": 5999.00, "stock": 14, "rating": 4.1, "description": "Personal tower air cooler with mult-directional wheels, 12L tank, and blower.", "discount": 15}
]

# 4. Color map for category gradient generator
CATEGORY_COLORS = {
    "electronics": ("#0f2027", "#203a43", "Electronics"),
    "fashion": ("#da4453", "#89216b", "Fashion"),
    "home-kitchen": ("#e65c00", "#f9d423", "Home & Kitchen"),
    "books-media": ("#000428", "#004e92", "Books & Media"),
    "sports-outdoors": ("#11998e", "#38ef7d", "Sports"),
    "smartphones": ("#1e3c72", "#2a5298", "Smartphones"),
    "laptops": ("#3a6073", "#16222f", "Laptops"),
    "footwear": ("#f12711", "#f5af19", "Footwear"),
    "beauty": ("#ff9a9e", "#fecfef", "Beauty"),
    "gaming": ("#7f00ff", "#e100ff", "Gaming"),
    "groceries": ("#1d976c", "#93f9b9", "Groceries"),
    "furniture": ("#3e2723", "#5d4037", "Furniture"),
    "fitness": ("#ff8c00", "#e52d27", "Fitness"),
    "books": ("#4b6cb7", "#182848", "Books"),
    "accessories": ("#134e5e", "#71b280", "Accessories"),
    "appliances": ("#2c3e50", "#3498db", "Appliances")
}

def generate_seed_image(product_name, category_slug, filepath):
    """
    Generates a premium looking e-commerce style typography gradient product card.
    Perfect for populating catalogs when model API requests are exhausted or restricted.
    """
    width, height = 400, 400
    img = Image.new('RGB', (width, height))
    draw = ImageDraw.Draw(img)
    
    # Grab colors from map
    colors = CATEGORY_COLORS.get(category_slug, ("#1e3c72", "#2a5298", "Products"))
    c1 = tuple(int(colors[0].lstrip('#')[i:i+2], 16) for i in (0, 2, 4))
    c2 = tuple(int(colors[1].lstrip('#')[i:i+2], 16) for i in (0, 2, 4))
    cat_label = colors[2].upper()
    
    # Draw vertical gradient background
    for y in range(height):
        r = int(c1[0] + (c2[0] - c1[0]) * y / height)
        g = int(c1[1] + (c2[1] - c1[1]) * y / height)
        b = int(c1[2] + (c2[2] - c1[2]) * y / height)
        draw.line([(0, y), (width, y)], fill=(r, g, b))
        
    # Set up fonts
    font_paths = [
        r"C:\Windows\Fonts\segoeui.ttf",
        r"C:\Windows\Fonts\arial.ttf",
        r"C:\Windows\Fonts\calibri.ttf"
    ]
    font_title = None
    font_sub = None
    for fp in font_paths:
        if os.path.exists(fp):
            try:
                font_title = ImageFont.truetype(fp, 26)
                font_sub = ImageFont.truetype(fp, 16)
                break
            except Exception:
                pass
    if not font_title:
        font_title = ImageFont.load_default()
        font_sub = ImageFont.load_default()

    # Draw small category label at top
    draw.text((30, 40), cat_label, fill=(255, 255, 255, 180), font=font_sub)
    draw.line([(30, 65), (100, 65)], fill=(255, 255, 255, 150), width=2)
    
    # Wrap text for title
    words = product_name.split(' ')
    lines = []
    current_line = ""
    for word in words:
        test_line = f"{current_line} {word}".strip()
        if font_title:
            try:
                bbox = font_title.getbbox(test_line)
                line_w = bbox[2] - bbox[0]
            except AttributeError:
                line_w = len(test_line) * 12
        else:
            line_w = len(test_line) * 12
            
        if line_w < (width - 60):
            current_line = test_line
        else:
            if current_line:
                lines.append(current_line)
            current_line = word
    if current_line:
        lines.append(current_line)
        
    # Draw product title lines
    y_text = 150
    for line in lines[:4]:
        draw.text((30, y_text), line, fill=(255, 255, 255), font=font_title)
        y_text += 40
        
    # Draw branding at bottom
    draw.text((30, 320), "OFFICIAL BRAND ITEM", fill=(255, 255, 255, 140), font=font_sub)
    draw.text((30, 345), "NEXUS SECURED PRODUCT", fill=(255, 255, 255, 100), font=font_sub)
    
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    img.save(filepath, 'JPEG', quality=95)
