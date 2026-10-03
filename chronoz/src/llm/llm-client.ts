import "dotenv/config";
import OpenAI from "openai";


const provider =
    process.env.CHRONOZ_LLM_PROVIDER?.trim() || "nvidia";


if (
    provider !== "openrouter" &&
    provider !== "ollama" &&
    provider !== "nvidia" &&
    provider !== "gemini"
) {
    throw new Error(
        "Unsupported CHRONOZ_LLM_PROVIDER."
    );
}


const providerConfig = {

    openrouter: {
        apiKey: process.env.OPENROUTER_API_KEY,
        baseURL:
            process.env.OPENROUTER_BASE_URL?.trim()
            || "https://openrouter.ai/api/v1",
        defaultModel: "openrouter/free",
        keyName: "OPENROUTER_API_KEY"
    },

    ollama: {
        apiKey: "ollama",
        baseURL:
            process.env.OLLAMA_BASE_URL?.trim()
            || "http://localhost:11434/v1",
        defaultModel: "qwen3:4b",
        keyName: ""
    },

    gemini: {
        apiKey: process.env.GEMINI_API_KEY,
        baseURL:
            process.env.GEMINI_BASE_URL?.trim()
            || "https://generativelanguage.googleapis.com/v1beta/openai/",
        defaultModel: "gemini-3.8-flash",
        keyName: "GEMINI_API_KEY"
    },

    nvidia: {
        apiKey: process.env.NVIDIA_API_KEY,
        baseURL:
            process.env.NVIDIA_BASE_URL?.trim()
            || "https://integrate.api.nvidia.com/v1",
        defaultModel:
            "nvidia/nemotron-3.5-lightning-30b-a3b",
        keyName: "NVIDIA_API_KEY"
    }

}[provider];


const {
    apiKey,
    baseURL
} = providerConfig;


if (!apiKey) {
    throw new Error(
        `${providerConfig.keyName} is missing.`
    );
}


export const llmModel =
    process.env.CHRONOZ_LLM_MODEL?.trim()
    || providerConfig.defaultModel;


export const llmConfig = {
    provider,
    model: llmModel,
    baseURL
};


const client = new OpenAI({
    apiKey,
    baseURL
});


type JsonSchemaFormat = {

    type: "json_schema";

    name: string;

    strict?: boolean;

    schema: Record<string, unknown>;
};


type ClassificationRequest = {

    model: string;

    instructions?: string;

    input: string;

    text?: {
        format?: JsonSchemaFormat;
    };
};


async function createNvidiaResponse(
    request: ClassificationRequest
): Promise<{ output_text: string }> {


    const response =
        await client.chat.completions.create({

            model:
                request.model,

            messages: [

                ...(request.instructions
                    ? [
                        {
                            role: "system" as const,
                            content: request.instructions
                        }
                    ]
                    : []),

                {
                    role: "user" as const,
                    content: request.input
                }

            ],

            temperature: 0.1,

            max_tokens: 2000,

            ...(request.text?.format
                ? {
                    response_format: {
                        type: "json_schema" as const,

                        json_schema: {
                            name:
                                request.text.format.name,

                            strict:
                                request.text.format.strict ?? true,

                            schema:
                                request.text.format.schema
                        }
                    }
                }
                : {})
        });


    const choice =
        response.choices[0];


    const content =
        choice?.message?.content;


    if (!content) {

        throw new Error(
            "NVIDIA returned an empty response."
        );
    }


    if (
        choice.finish_reason === "length"
    ) {

        throw new Error(
            "NVIDIA response was truncated before completion."
        );
    }


    return {
        output_text: content
    };
}


export const llmClient =

    provider === "nvidia"

        ? {
            responses: {
                create:
                    createNvidiaResponse
            }
        }

        : client;