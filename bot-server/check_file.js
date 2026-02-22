const fs = require('fs');
const path = require('path');

// ดูไฟล์ทั้งหมดในโฟลเดอร์ปัจจุบัน
const dirPath = __dirname;
console.log(`📂 Checking files in: ${dirPath}`);

const files = fs.readdirSync(dirPath);
console.log("📜 List of files found:");
files.forEach(file => {
    if (file.startsWith('.env')) {
        console.log(`   👉 Found potential env file: "${file}"`);
    } else {
        console.log(`   - ${file}`);
    }
});

// ลองอ่านไฟล์ .env โดยตรง
const envPath = path.join(dirPath, '.env');
if (fs.existsSync(envPath)) {
    console.log("\n✅ SUCCESS: Found '.env' file exactly!");
    const content = fs.readFileSync(envPath, 'utf-8');
    console.log("--- Content Preview ---");
    console.log(content.substring(0, 50) + "..."); // โชว์ 50 ตัวอักษรแรก
} else {
    console.log("\n❌ FAIL: Node.js CANNOT find '.env'");
    console.log("   (Most likely it is named '.env.txt')");
}