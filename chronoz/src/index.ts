import "dotenv/config";

import {
    readMarkdown,
    extractResearchCards
} from "./engine/extract-evidence";

import {
    encodeResearchCard
} from "./engine/classify-finding";

import type { ResearchEncoding } from "./types/finding";


async function main() {

    const filePath = process.argv[2];

    if (!filePath) {
        console.error(
            "Usage: npx.cmd tsx chronoz/src/index.ts <markdown-file>"
        );

        process.exit(1);
    }


    try {

        // 1. Read the research input
        const source = await readMarkdown(filePath);


        // 2. Extract Research Cards
        const cards = extractResearchCards(source);


        if (cards.length === 0) {
            console.log(
                "\nNo Research Cards found."
            );

            return;
        }


        console.log(
            `\nResearch Cards detected: ${cards.length}`
        );


        // 3. Store successful semantic encodings
        const encodings: ResearchEncoding[] = [];


        // 4. Store failed card IDs
        const failedCardIds: string[] = [];


        // 5. Encode each Research Card
        for (const card of cards) {

            console.log(
                `\n==============================`
            );

            console.log(
                `Research Card: ${card.id}`
            );

            console.log(
                `==============================`
            );


            console.log(
                "\nHighlight:"
            );

            console.log(
                card.highlight
            );


            console.log(
                "\nContext:"
            );

            console.log(
                card.context
            );


            try {

                const encoding =
                    await encodeResearchCard(card);


                encodings.push(
                    encoding
                );


                console.log(
                    "\nLLM Semantic Encoding:"
                );


                console.log(
                    JSON.stringify(
                        encoding,
                        null,
                        2
                    )
                );


            } catch (error) {

                failedCardIds.push(
                    card.id
                );


                console.error(
                    `\nFailed to encode ${card.id}`
                );


                if (error instanceof Error) {

                    console.error(
                        error.message
                    );

                } else {

                    console.error(
                        error
                    );
                }
            }
        }


        // 6. Determine overall run status
        let runStatus:
            | "completed"
            | "partial_success"
            | "failed";


        if (encodings.length === 0) {

            runStatus = "failed";

        } else if (
            failedCardIds.length > 0
        ) {

            runStatus = "partial_success";

        } else {

            runStatus = "completed";
        }


        // 7. Print run summary
        console.log(
            "\n=============================="
        );

        console.log(
            "CHronoZ Semantic Encoding Run"
        );

        console.log(
            "=============================="
        );


        console.log(
            `Source: ${source.fileName}`
        );

        console.log(
            `Cards detected: ${cards.length}`
        );

        console.log(
            `Cards encoded: ${encodings.length}`
        );

        console.log(
            `Cards failed: ${failedCardIds.length}`
        );

        console.log(
            `Run status: ${runStatus}`
        );


        if (
            failedCardIds.length > 0
        ) {

            console.log(
                "\nFailed Cards:"
            );


            for (
                const id of failedCardIds
            ) {

                console.log(
                    `- ${id}`
                );
            }
        }


        // 8. Final structured result
        const result = {

            runStatus,

            sourceFile:
                source.fileName,

            cardsDetected:
                cards.length,

            cardsEncoded:
                encodings.length,

            cardsFailed:
                failedCardIds.length,

            failedCardIds,

            encodings
        };


        console.log(
            "\nFinal Semantic Encoding Result:"
        );


        console.log(
            JSON.stringify(
                result,
                null,
                2
            )
        );


    } catch (error) {

        console.error(
            "\nCHronoZ Failed:"
        );


        if (error instanceof Error) {

            console.error(
                error.message
            );

        } else {

            console.error(
                error
            );
        }


        process.exit(1);
    }
}


main();