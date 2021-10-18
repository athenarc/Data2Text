"""
This cmd tool inputs an inference table downloaded from wandb (.json). It then
iteratively requests human evaluation for each one of the inferences.

Currently, the evaluator can make one of the following choices to evaluate the inference:
    1. Correct
    2. Confusion (confused on what some column name/value means)
    3. Omission (a column was not outputted in the inference
    4. Erroneous (a non-confusion mistake was made)
    5. Hallucination (the model add its own wrong info)
    6. Other, (specify)
"""
import argparse
import json
import os

from termcolor import colored

AVAILABLE_CHOICES = {
    1: "Correct",
    2: "Omission",
    3: "Erroneous",
    4: "Hallucination",
    # 5: "Other"
}


def parse_inference(inference_table):
    return {
        "target": inference_table[1],
        "predicted": inference_table[0],
        "source": inference_table[6]
    }


def show_inference(inference):
    print(colored("> Available choices:", color="cyan"))
    for ind, choice in AVAILABLE_CHOICES.items():
        print(f"{ind}. {choice}")
    print()
    print(f"{colored('Target', color='cyan')}: {inference['target']}")
    print(f"{colored('Predicted', color='cyan')}: {inference['predicted']}")
    print(f"{colored('Source', color='cyan')}: {inference['source']}")
    print()


def confirm_choice(evaluation):
    while True:
        print(f"> {colored('Chosen evaluation:', color='cyan')} {evaluation}")
        confirmed_str = input(colored("Confirm (y/n): ", color="green"))

        if confirmed_str.lower() == "y":
            return True
        elif confirmed_str.lower() == "n":
            return False
        else:
            continue


def choice_loop():
    while True:
        try:
            choices = input(colored("> Choice: ", color="cyan")).strip().split(",")
            choices = list(map(int, choices))
            for choice in choices:
                if choice < 1 or choice > len(AVAILABLE_CHOICES.items()):
                    raise ValueError
        except ValueError:
            print(f"Unexpected input, choose an integer from 1-{len(AVAILABLE_CHOICES.items())}")
            continue

        evaluation = ",".join(AVAILABLE_CHOICES[choice] for choice in choices)
        # if AVAILABLE_CHOICES[choice] == "Other":
        #     evaluation += f", {input(colored('> Explanation: ', color='cyan'))}"

        if not confirm_choice(evaluation):
            continue

        return evaluation


def main():
    parser = argparse.ArgumentParser(description="Inference human evaluator.")
    parser.add_argument(
        "-i", "--inferences", required=True, help="path to inferences file", type=str,
    )
    parser.add_argument(
        "-o", "--output", required=True, help="path to output human evaluation file (should not exist).", type=str,
    )
    args = parser.parse_args()

    with open(args.inferences) as f:
        inferences = json.load(f)["data"]

    if os.path.exists(args.output):
        raise FileExistsError("Output file should not exist.")

    evaluated_inferences = []
    for raw_inference in inferences:
        print("\n" + "-" * 90)
        print("-" * 90)
        inference = parse_inference(raw_inference)
        show_inference(inference)

        evaluation = choice_loop()
        inference['evaluation'] = evaluation
        evaluated_inferences.append(inference)

        with open(args.output, 'w') as fp:
            json.dump(evaluated_inferences, fp)

        print(f"Evaluations done: {len(evaluated_inferences)} / {len(inferences)}")


if __name__ == '__main__':
    main()
