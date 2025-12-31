#!/usr/bin/env node
import * as cdk from "aws-cdk-lib";

import {ConnectionsStack} from "./connections";
import {GitHubOidcStack} from "./github-oidc";

const app = new cdk.App();

const AWS_ACCOUNT = "578999165660";
const REGION = "us-east-1";
const DOMAIN_NAME = "connections.layertwo.dev";

const env = {
    account: AWS_ACCOUNT,
    region: REGION,
};

new GitHubOidcStack(app, "GitHubOidcStack", {
    env,
    githubOrg: "layertwo",
    githubRepo: "connections",
});

new ConnectionsStack(app, "ConnectionsStack", {
    env,
    domainName: DOMAIN_NAME,
});

app.synth();
