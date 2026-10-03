export type EvidenceSource = {
    sourceType: "markdown";
    sourcePath: string;
    fileName: string;
    content: string;
}

export type EvidenceItem = {
    id: string;
    text: string;
    sourceFile: string;
}

