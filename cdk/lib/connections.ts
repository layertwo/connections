import {Construct} from "constructs";

import {RemovalPolicy, Stack, StackProps} from "aws-cdk-lib";
import {Certificate} from "aws-cdk-lib/aws-certificatemanager";
import {CachePolicy, Distribution, ViewerProtocolPolicy} from "aws-cdk-lib/aws-cloudfront";
import {S3StaticWebsiteOrigin} from "aws-cdk-lib/aws-cloudfront-origins";
import {ARecord, HostedZone, RecordTarget} from "aws-cdk-lib/aws-route53";
import {CloudFrontTarget} from "aws-cdk-lib/aws-route53-targets";
import {BlockPublicAccess, Bucket} from "aws-cdk-lib/aws-s3";
import {BucketDeployment, Source} from "aws-cdk-lib/aws-s3-deployment";

export interface ConnectionsStackProps extends StackProps {
    domainName: string;
}

export class ConnectionsStack extends Stack {
    private readonly props: ConnectionsStackProps;
    private readonly bucket: Bucket;
    private readonly hostedZone: HostedZone;
    private readonly distribution: Distribution;

    constructor(scope: Construct, id: string, props: ConnectionsStackProps) {
        super(scope, id, props);
        this.props = props;

        this.bucket = this.buildBucket();
        this.hostedZone = this.createHostedZone();
        this.distribution = this.buildDistribution();
    }

    private buildBucket(): Bucket {
        return new Bucket(this, "ConnectionsBucket", {
            bucketName: "layertwo-connections-maps",
            websiteIndexDocument: "index.html",
            publicReadAccess: false,
            blockPublicAccess: BlockPublicAccess.BLOCK_ALL,
            removalPolicy: RemovalPolicy.RETAIN_ON_UPDATE_OR_DELETE,
        });
    }

    private createHostedZone(): HostedZone {
        return new HostedZone(this, "HostedZone", {
            zoneName: this.props.domainName,
        });
    }

    private buildDistribution(): Distribution {
        // Do certificate validation via email
        const certificate = new Certificate(this, "Certificate", {
            domainName: this.props.domainName,
        });

        // Create CloudFront distribution
        const distribution = new Distribution(this, "Distribution", {
            defaultBehavior: {
                origin: new S3StaticWebsiteOrigin(this.bucket),
                viewerProtocolPolicy: ViewerProtocolPolicy.REDIRECT_TO_HTTPS,
                cachePolicy: CachePolicy.CACHING_OPTIMIZED,
            },
            defaultRootObject: "index.html",
            domainNames: [this.props.domainName],
            certificate,
        });

        // Deploy files from output directory to S3
        new BucketDeployment(this, "DeployConnectionss", {
            sources: [Source.asset("../output")],
            destinationBucket: this.bucket,
            distribution,
            distributionPaths: ["/*"],
        });

        // Create A record pointing to CloudFront distribution
        new ARecord(this, "AliasRecord", {
            zone: this.hostedZone,
            recordName: this.props.domainName,
            target: RecordTarget.fromAlias(new CloudFrontTarget(distribution)),
        });

        return distribution;
    }
}
