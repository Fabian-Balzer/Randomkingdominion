"""The explanation texts of the quiz, shown on the start screen and in a popover
during a round."""

import streamlit as st

from .scoring import GOOD_SCORE_THRESHOLD, IMPRESSIVE_SCORE_THRESHOLD, MAX_ROUND_SCORE

QUIZ_INTRO = """Are you able to infer the engine qualities for a given kingdom? I highly recommend reading the instructions below before getting started. Note that this website is not optimized for mobile devices."""

EXPLANATIONS: dict[str, str] = {}
EXPLANATIONS[
    "❓ About this quiz"
] = """In this quiz, you get to try to infer the engine qualities for a given kingdom. 
This quiz is mainly just a silly little thing that I set up because I was curious about how well I would be able to guess these by only looking at the CSOs, so don't expect too much.

The kingdom plot is generated using a weird formula (see *Quality Calculation Details*), calculating the total quality for each of *Gain, Thinning, Draw, Village, Alt-VP* and *Attacks* based on the individual qualities of the CSOs that are part of it.

I do think that this might generally help you to analyze a given kingdom for its important aspects, but nonetheless some of the qualities are extremely subjective, and knowing a kingdom's qualities **still does not really tell you how to play it**; you merely sort of assess what to expect (and looking for +Buy, or more importantly the absence of it, can never hurt).

To take part in the quiz yourself, you only have to roll a kingdom and set the qualities to the values you think are right. I recommend reading through the *Tips and Tricks* section before starting.
"""

EXPLANATIONS["🧮 Quality Calculation Details"] = """
A total value in a kingdom is based on the CSOs' values of that quality, which individually can be 0, 1, 2 or 3, and in special, limited or luck-based cases (like Loots, Boons, Knights) also 0.5. The total value is then calculated based on the following rules:
- **0**: \\
If there are no CSOs with a value, then the total value is zero.
- **0.5**:\\
    If the highest value of a CSO is 0.5, then the total quality is 0.5.
- **1**:\\
    If there is at least one CSO with a value of 1, then the total quality is at least 1.
- **2**:\\
    If there is at least one CSO with a value of 2 OR there are 4 CSOs with a quality of 1, then the total quality is at least 2.
- **3**:\\
    If there is at least one CSO with a value of 3 OR there are 3 CSOs with a quality of 2 (to which also 4 CSOs with a 1-value count), then the total quality is at least 3.
- **4**:\\
    If there are 2 CSOs with a value of 3 (to which also 3 CSOs with a 2-value count), then the total quality is 4.
"""

EXPLANATIONS[
    "💡 Tips and Tricks"
] = """I highly recommend to read this section thoroughly before starting, and to make sure you've understood how a quality value is calculated (see the previous tab).
Go through the qualities one by one, looking at all CSOs in the kingdom (including extra stuff like a Ferryman or Riverboat card). Try to find the ones that might contribute to that quality, and then assess their strengths individually, finally combining them according to the formula.

Here are some specific tips for assessing each quality:

- **Gain**:
    - CSOs that provide +Buy and Workshops have a default Gain quality of 2. 
    - Stuff that gains just very specific things (like Bandit) or that only remodel have a Gain quality of 1.
- **Thinning**:
    - Remodel variants usually have a thinning quality of 1.
    - Most normal trashers have a thinning quality of 2 (like Sentry).
    - Only super strong thinners like Chapel or Donate default to 3.
- **Draw**:
    - The draw quality of a card also depends on whether it's terminal or not.
    - Most Smithy and Lab variants have a draw quality of 2.
    - Most Moat variants only have a draw quality of 1.
- **Village**:
    - Normal Village variants have a Village quality of 2, even if they decrease handsize.
    - Stuff limited to a single +Action per turn (e.g., Necropolis or Barracks), or conditional Villages (looking at Diplomat) have a Village quality of 1.
- **Alt-VP**:
    - Alt-VP qualities are given pretty generously; Anything being worth a flat 2 VP (like Tunnel or Island) is already a 2.
    - Stuff with very limited VP (like Mill or Wedding) have a quality of 1.
    - Note that Trashing and Cursing attacks also have an Alt-VP quality of 1.
- **Attacks**:
    - Most attacks have a quality of 2, unless they are pretty weak or situational (like Bandit, Marauder or Bridge Troll), in which case they have a quality of 1.
    - Centralizing nasty Attacks such as Witch, Swindler or Torturer have a quality of 3.
    - Note that even some non-Attack cards can have an Attack quality of 1 if they can mess with your deck or even your turn (Masquerade, Monkey, Possession).


If you completely disagree with a certain quality assessment, DM me on Discord :)

In case you want to read more, I have provided a few more insights and lists of all CSOs on the respective sites for each quality.
"""

EXPLANATIONS[
    "🏆 Scoring"
] = f"""The score awarded for completing the quiz is based on the offsets to the real values: For each quality, you are awarded 
- 2 points if you are correct, otherwise
- 1.5 points if you are off by at most 0.5 (only important for luck-based/limited qualities), otherwise
- 1 point if you are only off by at most 1, and
- 0 points if you are off by more than 1.
- You receive an additional 3 points for correctly assessing the Buy situation.

Out of the maximum of {MAX_ROUND_SCORE} points per kingdom, scoring anything above {GOOD_SCORE_THRESHOLD} points is pretty good, and above {IMPRESSIVE_SCORE_THRESHOLD} points is pretty impressive, but don't worry too much about the score - it's just for fun, and the main point is to train your ability to analyze kingdoms for their qualities, which is a skill that can be helpful when playing.
"""


@st.fragment
def st_build_explanation_selector() -> None:
    choice = st.segmented_control(
        "Explanations",
        list(EXPLANATIONS),
        default=None,
        width="stretch",
        label_visibility="collapsed",
    )
    if choice is not None:
        st.markdown(EXPLANATIONS[choice])


def st_build_explanation_section() -> None:
    """The intro and explanations for the start screen."""
    st.write(QUIZ_INTRO)
    with st.container(border=True):
        st_build_explanation_selector()
