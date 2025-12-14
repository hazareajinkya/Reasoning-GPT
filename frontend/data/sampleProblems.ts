export interface SampleProblem {
  id: string;
  title: string;
  problem: string;
}

export const sampleProblems: SampleProblem[] = [
  {
    id: "cat-2025-slot2-musicians",
    title: "CAT 2025 Slot 2 - Musicians & Gurus",
    problem: `**Instructions [25 - 29]**

Ananya Raga, Bhaskar Tala, Charu Veena, and Devendra Sur are four musicians. Each of them started and completed their training as students under each of three Gurus — Pandit Meghnath, Ustad Samiran, and Acharya Raghunath between 2013 and 2024, including both the years. Each Guru trains any student for consecutive years only, for a span of 2, 3, or 4 years, with each Guru having a different span. During some of these years, a student may not have trained under these Gurus; however, they never trained under multiple Gurus in the same year. In none of these years, any of these Gurus trained more than two of these students at the same time. When two students train under the same Guru at the same time, they are referred to as Gurubhai, irrespective of their gender.

The following additional facts are known.

1. Ustad Samiran never trained more than one of these students in the same year.
2. Acharya Raghunath did not train any of these students during 2015-2018, as well as during 2021-24.
3. Ananya and Devendra were never Gurubhai; neither were Bhaskar and Charu. All other pairs of musicians were Gurubhai for exactly 2 years.
4. In 2013, Ananya and Bhaskar started their trainings under Pandit Meghnath and under Ustad Samiran, respectively.

**25.** In which of the following years were Ananya and Bhaskar Gurubhai?
**A** 2020
**B** 2018
**C** 2021
**D** 2014

**26.** In which year did Charu begin her training under Pandit Meghnath?
**A** 2017
**B** 2015
**C** 2021
**D** 2016

**27.** In which of the following years were Bhaskar and Devendra Gurubhai?
**A** 2022
**B** 2015
**C** 2020
**D** 2018

**28.** Which of the following statements is TRUE?
**A** Charu was training under Ustad Samiran in 2018.
**B** Ananya was training under Ustad Samiran in 2015.
**C** Ananya was training under Ustad Samiran in 2018.
**D** Charu was training under Ustad Samiran in 2019.

**29.** In how many of the years between 2013-24, were only two of these four musicians training under these Gurus?`
  },
  {
    id: "cat-2025-slot2-balls-hoops",
    title: "CAT 2025 Slot 2 - Balls & Hoops",
    problem: `There are six spherical balls, B1, B2, B3, B4, B5, and B6, and four circular hoops H1, H2, H3, and H4.
Each ball was tested on each hoop once, by attempting to pass the ball through the hoop. If the diameter of a ball is not larger than the diameter of the hoop, the ball passes through the hoop and makes a "ping". Any ball having a diameter larger than that of the hoop gets stuck on that hoop and does not make a ping.

The following additional information is known:

1. B1 and B6 each made a ping on H4, but B5 did not.
2. B4 made a ping on H3, but B1 did not.
3. All balls, except B3, made pings on H1.
4. None of the balls, except B2, made a ping on H2.

**5.** What was the total number of pings made by B1, B2, and B3?

**6.** Which of the following statements about the relative sizes of the balls is NOT NECESSARILY true?
**A** B4 < B5 < B3
**B** B2 < B1 < B5
**C** B1 < B6 < B3
**D** B1 < B5 < B3

**7.** Which of the following statements about the relative sizes of the hoops is true?
**A** H2 < H3 < H4 < H1
**B** H1 < H3 < H4 < H2
**C** H1 < H4 < H3 < H2
**D** H2 < H4 < H3 < H1

**8.** What BEST can be said about the total number of pings from all the tests undertaken?
**A** 12 or 13
**B** 13 or 14
**C** 12 or 13 or 14
**D** At least 9`
  },
  {
    id: "cat-2024-slot1-quiet",
    title: "CAT 2024 Slot 1 - QUIET Tournament",
    problem: `The game of QUIET is played between two teams. Six teams, numbered 1, 2, 3, 4, 5, and 6, play in a QUIET tournament. These teams are divided equally into two groups. In the tournament, each team plays every other team in the same group only once, and each team in the other group exactly twice. The tournament has several rounds, each of which consists of a few games. Every team plays exactly one game in each round.

The following additional facts are known about the schedule of games in the tournament.

1. Each team played against a team from the other group in Round 8.
2. In Round 4 and Round 7, the match-ups, that is the pair of teams playing against each other, were identical. In Round 5 and Round 8, the match-ups were identical.
3. Team 4 played Team 6 in both Round 1 and Round 2.
4. Team 1 played Team 5 ONLY once and that was in Round 2.
5. Team 3 played Team 4 in Round 3. Team 1 played Team 6 in Round 6.
6. In Round 8, Team 3 played Team 6, while Team 2 played Team 5.

**9.** How many rounds were there in the tournament?

**10.** What is the number of the team that played Team 1 in Round 5?

**1.** Which team among the teams numbered 2, 3, 4, and 5 was not part of the same group?
**A** 5
**B** 3
**C** 4
**D** 2

**2.** What is the number of the team that played Team 1 in Round 7?

**3.** What is the number of the team that played Team 6 in Round 3?`
  }
];

