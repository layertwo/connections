import {Construct} from "constructs";

import {RemovalPolicy, Stack, StackProps} from "aws-cdk-lib";
import {Certificate, CertificateValidation} from "aws-cdk-lib/aws-certificatemanager";
import {
    CachePolicy,
    Distribution,
    S3OriginAccessControl,
    Signing,
    ViewerProtocolPolicy,
} from "aws-cdk-lib/aws-cloudfront";
import {S3BucketOrigin} from "aws-cdk-lib/aws-cloudfront-origins";
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
            blockPublicAccess: BlockPublicAccess.BLOCK_ALL,
            removalPolicy: RemovalPolicy.RETAIN_ON_UPDATE_OR_DELETE,
            enforceSSL: true,
            minimumTLSVersion: 1.2,
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
            validation: CertificateValidation.fromDns(this.hostedZone),
        });

        const oac = new S3OriginAccessControl(this, "OAC", {
            signing: Signing.SIGV4_ALWAYS
        });

        // Create CloudFront distribution
        const distribution = new Distribution(this, "Distribution", {
            defaultBehavior: {
                origin: S3BucketOrigin.withOriginAccessControl(this.bucket, {
                    originAccessControl: oac,
                }),
                viewerProtocolPolicy: ViewerProtocolPolicy.REDIRECT_TO_HTTPS,
                cachePolicy: CachePolicy.CACHING_OPTIMIZED,
            },
            defaultRootObject: "index.html",
            domainNames: [this.props.domainName],
            certificate,
        });

        // Deploy files from output directory to S3
        new BucketDeployment(this, "BucketDeployment", {
            sources: [Source.asset("../output")],
            destinationBucket: this.bucket,
            distribution,
            distributionPaths: ["/*"],
            prune: true,
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
