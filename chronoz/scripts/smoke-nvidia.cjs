const { llmClient, llmModel, llmConfig } = require('../src/llm/llm-client.ts');

console.log(llmConfig);
if (llmConfig.provider !== 'nvidia') {
    console.error('Set CHRONOZ_LLM_PROVIDER=nvidia before running this test.');
    process.exit(1);
}

const timer = setTimeout(() => {
    console.error('NVIDIA smoke test timed out after 30 seconds.');
    process.exit(1);
}, 30000);

llmClient.responses.create({
    model: llmModel,
    instructions: 'Return only valid JSON containing ok: true.',
    input: 'Test the connection.',
    text: { format: {
        type: 'json_schema', name: 'connection_test', strict: true,
        schema: {
            type: 'object', properties: { ok: { type: 'boolean' } },
            required: ['ok'], additionalProperties: false
        }
    } }
}).then(response => {
    if (JSON.parse(response.output_text).ok !== true) {
        throw new Error('Unexpected smoke test output.');
    }
    console.log('PASS: NVIDIA Chat Completions and structured JSON.');
}).catch(error => {
    const message = String(error.message).replaceAll(process.env.NVIDIA_API_KEY, '[REDACTED]');
    console.error(`NVIDIA error (HTTP ${error.status ?? 'none'}): ${message}`);
    process.exitCode = 1;
}).finally(() => clearTimeout(timer));
