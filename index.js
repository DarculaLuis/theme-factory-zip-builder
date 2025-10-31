import express from "express";
import cors from "cors";
import AdmZip from "adm-zip";
import fs from "fs";
import path from "path";

const app = express();
app.use(cors());
app.use(express.json({ limit: "10mb" }));

const PORT = process.env.PORT || 3000;
const outputDir = "./files";
if (!fs.existsSync(outputDir)) fs.mkdirSync(outputDir);

app.post("/build", (req, res) => {
  try {
    const { theme_name, files } = req.body;
    if (!theme_name || !files) {
      return res.status(400).json({ error: "Missing theme_name or files" });
    }

    const zip = new AdmZip();
    Object.entries(files).forEach(([filename, content]) => {
      zip.addFile(filename, Buffer.from(content, "utf8"));
    });

    const zipPath = path.join(outputDir, `${theme_name}.zip`);
    zip.writeZip(zipPath);

    const publicUrl = `https://${req.headers.host}/files/${theme_name}.zip`;
    res.json({ download_url: publicUrl });
  } catch (error) {
    console.error("Error:", error);
    res.status(500).json({ error: "Server error" });
  }
});

app.use("/files", express.static("files"));

app.listen(PORT, () => console.log(`ZIP Builder running on port ${PORT}`));
