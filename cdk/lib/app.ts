#!/usr/bin/env node
import * as cdk from "aws-cdk-lib";

import {ConnectionsStack} from "./connections";
import {GitHubOidcStack} from "./github-oidc";

const app = new cdk.App();

const REGION = "us-east-1";
const DOMAIN_NAME = "connections.layertwo.dev";

new GitHubOidcStack(app, "GitHubOidcStack", {
    env: {
        account: process.env.CDK_DEFAULT_ACCOUNT,
        region: REGION,
    },
    githubOrg: "layertwo",
    githubRepo: "connections",
});

new ConnectionsStack(app, "ConnectionsStack", {
    env: {
        account: process.env.CDK_DEFAULT_ACCOUNT,
        region: REGION,
    },
    domainName: DOMAIN_NAME,
});

app.synth();
