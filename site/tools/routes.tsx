import type { ReactElement } from "react"
import { Layout } from "@/Layout"
import {
  AwarderPage, AwardersList, AwardPage, ChallengePage, ChallengesList,
  Home, RecipientPage, RecipientsList,
} from "@/pages"
import { awarders, awards, challenges, recipients } from "@/lib/dpc"

export type Route = { path: string; title: string; element: ReactElement }

/** Every page the site has, derived from the exported JSON.
 *
 *  This is the direct equivalent of Hugo's content adapters: one list of
 *  routes, built from the same data, rather than thousands of stub files. */
export function routes(): Route[] {
  const all: Route[] = [
    { path: "/", title: "DPChallenge Award Gallery", element: <Layout><Home /></Layout> },
    { path: "/awarders/", title: "Awarders", element: <Layout active="Awarders"><AwardersList /></Layout> },
    { path: "/challenges/", title: "Challenges", element: <Layout active="Challenges"><ChallengesList /></Layout> },
    { path: "/recipients/", title: "Recipients", element: <Layout active="Recipients"><RecipientsList /></Layout> },
  ]

  for (const a of awarders) {
    all.push({
      path: `/awarders/${a.slug}/`,
      title: `Awards given by ${a.name}`,
      element: <Layout active="Awarders"><AwarderPage slug={a.slug} /></Layout>,
    })
  }
  for (const award of awards) {
    all.push({
      path: `/awarders/${award.awarder_slug}/${award.slug}/`,
      title: award.name,
      element: <Layout active="Awarders"><AwardPage award={award} /></Layout>,
    })
  }
  for (const c of challenges) {
    all.push({
      path: `/challenges/${c.slug}/`,
      title: c.name,
      element: <Layout active="Challenges"><ChallengePage challenge={c} /></Layout>,
    })
  }
  for (const r of recipients) {
    all.push({
      path: `/recipients/${r.slug}/`,
      title: `${r.name}'s gallery`,
      element: <Layout active="Recipients"><RecipientPage person={r} /></Layout>,
    })
  }
  return all
}
