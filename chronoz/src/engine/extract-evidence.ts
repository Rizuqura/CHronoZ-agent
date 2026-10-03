import { readFile } from "node:fs/promises";
import { basename, extname, resolve } from "node:path";

import type {EvidenceItem, EvidenceSource} from "../types/evidence";

export async function readMarkdown(filePath: string): Promise<EvidenceSource> {
    const absolutePath = resolve(filePath);
    const extension = extname(absolutePath).toLowerCase();

    if (extension !== ".md") {
        throw new Error(`unsupported file type: ${extension || "unknown"}. Only .md files are supported.`);
    }       

    const content = await readFile(absolutePath, "utf-8");

    return {
        sourceType: "markdown",
        sourcePath: absolutePath,
        fileName: basename(absolutePath),
        content
    }
}

export function extractEvidence(
    source: EvidenceSource
): EvidenceItem[] {
    const blocks = source.content.split(/\n\s*\n/)
    .map((block) => block.trim())
    .filter((block) => block.length > 0 && 
    !block.startsWith("#")
    );

    return blocks.map((text, index) => ({
        id: `ev-${String(index+1).padStart(3, "0")}`,
        text,
        sourceFile: source.fileName
    }));
}

export type ResearchCard = {
    id: string;
    highlight: string;
    context: string;
};

export function extractResearchCard(
    markdown : string
): ResearchCard[] {
    const cards : ResearchCard[] = [];
    const cardBlocks = markdown.split(/^## Research Card:/m).slice(1);

    for (const block of cardBlocks) {
        const trimmedBlock = block.trim();
        const lines = trimmedBlock.split("\n");
        const id = lines [0].trim();

        const highlightMarker = "### Highlight"
        const contextMarker = "### Context"

        const highlightStart = trimmedBlock.indexOf(highlightMarker);
        const contextStart = trimmedBlock.indexOf(contextMarker);

        if(highlightStart === -1 || contextStart === -1) {
            continue
        }

        const highlight = trimmedBlock.slice(
            highlightStart + highlightMarker.length, contextStart
        ).trim();

        const context = trimmedBlock.slice(
            contextStart + contextMarker.length
        ).trim();

        cards.push({
        id, highlight, context
        });
    }
    return cards;
}

export function extractResearchCards(source: EvidenceSource): ResearchCard[] {
    return extractResearchCard(source.content);
}
    
